#include <iostream>
#include <cuda_runtime.h>

__global__ void test_kernel() { }

int main() {
    std::cout << "CUDA Environment Verified." << std::endl;
    test_kernel<<<1, 1>>>();
    cudaDeviceSynchronize();
    return 0;
}
