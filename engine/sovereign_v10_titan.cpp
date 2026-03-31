#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>
#include <random>
#include <string>
#include <fstream>
#include <cstring>
#include <ctime>
#include <omp.h>
#include "tokenizer.h"

// --- DIMENSIONS ---
static const int VOCAB = 5000;
static const int EMBED_DIM = 64;
static const int H_DIM = 256;
static const int GRU_CONCAT = EMBED_DIM + H_DIM;
static const int FFN_IN = EMBED_DIM + H_DIM;
static const int HIDDEN = 256;

// --- UTILS ---
inline double relu(double x) { return x > 0 ? x : 0; }
inline double sigmoid(double x) { return 1.0 / (1.0 + std::exp(-x)); }
void softmax(double* l, double* p, int s) {
    double m = l[0]; for(int i=1; i<s; i++) if(l[i]>m) m=l[i];
    double sum = 0; for(int i=0; i<s; i++) { p[i] = std::exp(l[i]-m); sum += p[i]; }
    for(int i=0; i<s; i++) p[i] /= sum;
}

// --- ENGINE ---
struct SovereignBlock {
    double (*We)[EMBED_DIM];
    double (*Wz)[GRU_CONCAT]; double *bz;
    double (*Wr)[GRU_CONCAT]; double *br;
    double (*Wh)[GRU_CONCAT]; double *bh;
    double (*w1)[FFN_IN];     double *b1;
    double (*Wo)[HIDDEN];     double (*Whw)[H_DIM]; double *bo;

    SovereignBlock() {
        We = new double[VOCAB][EMBED_DIM];
        Wz = new double[H_DIM][GRU_CONCAT]; bz = new double[H_DIM];
        Wr = new double[H_DIM][GRU_CONCAT]; br = new double[H_DIM];
        Wh = new double[H_DIM][GRU_CONCAT]; bh = new double[H_DIM];
        w1 = new double[HIDDEN][FFN_IN];    b1 = new double[HIDDEN];
        Wo = new double[VOCAB][HIDDEN]; Whw = new double[VOCAB][H_DIM]; bo = new double[VOCAB];
    }
    void load(const char* p) {
        std::ifstream f(p, std::ios::binary); if(!f) return;
        int hdr[4]; f.read((char*)hdr, 16);
        f.read((char*)We, 8*VOCAB*EMBED_DIM); f.read((char*)Wz, 8*H_DIM*GRU_CONCAT); f.read((char*)bz, 8*H_DIM);
        f.read((char*)Wr, 8*H_DIM*GRU_CONCAT); f.read((char*)br, 8*H_DIM); f.read((char*)Wh, 8*H_DIM*GRU_CONCAT); f.read((char*)bh, 8*H_DIM);
        f.read((char*)w1, 8*HIDDEN*FFN_IN); f.read((char*)b1, 8*HIDDEN); f.read((char*)Wo, 8*VOCAB*HIDDEN); f.read((char*)Whw, 8*VOCAB*H_DIM); f.read((char*)bo, 8*VOCAB);
    }
};

struct Agent {
    SovereignBlock* m;
    double h[H_DIM];
    std::mt19937 gen;
    Agent(SovereignBlock* master, int seed) : m(master), gen(seed) { std::memset(h, 0, 8*H_DIM); }
};

static WordTokenizer* g_tok = nullptr;

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

extern "C" {
    EXPORT void* sovereign_init_master() {
        if(!g_tok) { g_tok = new WordTokenizer(); g_tok->load_vocab("vocab.txt"); }
        SovereignBlock* b = new SovereignBlock(); b->load("master_brain.bin");
        return (void*)b;
    }

    EXPORT void* sovereign_init_agent(const char* name, void* master, int seed) {
        return (void*)new Agent((SovereignBlock*)master, seed);
    }

    EXPORT void sovereign_agent_observe(void* agent, const char* text) {
        Agent* a = (Agent*)agent;
        std::vector<int> tokens = g_tok->encode(text);
        for(int t : tokens) {
            double gru_in[EMBED_DIM]; std::memcpy(gru_in, a->m->We[t], 8*EMBED_DIM);
            double h_new[H_DIM];
            for(int i=0; i<H_DIM; i++) {
                double pz = a->m->bz[i], pr = a->m->br[i];
                for(int j=0; j<EMBED_DIM; j++) { pz += a->m->Wz[i][j]*gru_in[j]; pr += a->m->Wr[i][j]*gru_in[j]; }
                for(int j=0; j<H_DIM; j++) { pz += a->m->Wz[i][EMBED_DIM+j]*a->h[j]; pr += a->m->Wr[i][EMBED_DIM+j]*a->h[j]; }
                double z = sigmoid(pz), r = sigmoid(pr);
                double phc = a->m->bh[i];
                for(int j=0; j<EMBED_DIM; j++) phc += a->m->Wh[i][j]*gru_in[j];
                for(int j=0; j<H_DIM; j++) phc += a->m->Wh[i][EMBED_DIM+j]*(r*a->h[j]);
                h_new[i] = (1.0-z)*a->h[i] + z*std::tanh(phc);
            }
            std::memcpy(a->h, h_new, 8*H_DIM);
        }
    }

    EXPORT const char* sovereign_agent_act(void* agent, int max_len, double temp) {
        Agent* a = (Agent*)agent;
        std::vector<int> response;
        int last_tok = TOK_START;
        
        static char out[4096];
        for(int i=0; i<max_len; i++) {
            double gru_in[EMBED_DIM]; std::memcpy(gru_in, a->m->We[last_tok], 8*EMBED_DIM);
            double h_new[H_DIM], a1[HIDDEN], logits[VOCAB], probs[VOCAB];
            for(int k=0; k<H_DIM; k++) {
                double pz = a->m->bz[k], pr = a->m->br[k];
                for(int j=0; j<EMBED_DIM; j++) { pz += a->m->Wz[k][j]*gru_in[j]; pr += a->m->Wr[k][j]*gru_in[j]; }
                for(int j=0; j<H_DIM; j++) { pz += a->m->Wz[k][EMBED_DIM+j]*a->h[j]; pr += a->m->Wr[k][EMBED_DIM+j]*a->h[j]; }
                double z = sigmoid(pz), r = sigmoid(pr), phc = a->m->bh[k];
                for(int j=0; j<EMBED_DIM; j++) phc += a->m->Wh[k][j]*gru_in[j];
                for(int j=0; j<H_DIM; j++) phc += a->m->Wh[k][EMBED_DIM+j]*(r*a->h[j]);
                h_new[k] = (1.0-z)*a->h[k] + z*std::tanh(phc);
            }
            std::memcpy(a->h, h_new, 8*H_DIM);
            for(int k=0; k<HIDDEN; k++) {
                double v = a->m->b1[k];
                for(int j=0; j<EMBED_DIM; j++) v += gru_in[j]*a->m->w1[k][j];
                for(int j=0; j<H_DIM; j++) v += h_new[j]*a->m->w1[k][EMBED_DIM+j];
                a1[k] = relu(v);
            }
            for(int v=0; v<VOCAB; v++) {
                double s = a->m->bo[v];
                for(int k=0; k<HIDDEN; k++) s += a1[k]*a->m->Wo[v][k];
                for(int k=0; k<H_DIM; k++) s += h_new[k]*a->m->Whw[v][k];
                logits[v] = s / (temp + 1e-6);
            }
            softmax(logits, probs, VOCAB);
            std::discrete_distribution<int> d(probs, probs+VOCAB);
            int next = d(a->gen);
            if(next == TOK_END) break;
            response.push_back(next); last_tok = next;
        }
        std::string res = g_tok->decode(response);
        std::strncpy(out, res.c_str(), 4095);
        return out;
    }

    EXPORT void sovereign_free_master(void* m) { delete (SovereignBlock*)m; }
    EXPORT void sovereign_free_agent(void* a) { delete (Agent*)a; }
}
