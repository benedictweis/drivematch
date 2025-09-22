#pragma once

#include <random>
#include <string>

inline std::string generateUUID() {
    static std::random_device rd;
    static std::mt19937_64 gen(rd());
    static std::uniform_int_distribution<uint64_t> dis;
    return std::to_string(dis(gen));
}