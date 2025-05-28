#include "httplib.h"
#include <random>
#include <string>
#include <thread>
#include <mutex>
#include <chrono>
#include <iostream>
using namespace httplib;

std::mutex data_mutex;
std::string data1, data2;

void generate_data() {
    std::lock_guard<std::mutex> lock(data_mutex);
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis('A', 'Z');
    data1 = std::string(51, ' ');
    data2 = std::string(51, ' ');
    for (int i = 0; i < 51; ++i) {
        data1[i] = static_cast<char>(dis(gen));
        data2[i] = static_cast<char>(dis(gen));
    }
}

int main() {
  std::thread updater([&]() {
      while (true) {
          generate_data();
          std::this_thread::sleep_for(std::chrono::seconds(60));
      }
  });

  Server svr;
  svr.Get("/data.txt", [](const Request&, Response& res) {
    std::lock_guard<std::mutex> lock(data_mutex);
    res.set_content(data1 + "\n" + data2, "text/plain");
  });
  svr.listen("localhost", 8080);
  return 0;
}
