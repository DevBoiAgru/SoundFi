#include <iostream>
#include <SFML/Audio.hpp>
#include <cmath>
#include <fstream>

constexpr int SAMPLE_RATE = 44100;
constexpr double PI = 3.14159265359;
constexpr float BIT_DURATION = 0.02;                    // Duration of the beep for 1 bit
constexpr int TRUE_FREQ = 7000, FALSE_FREQ = 6800;      // Frequencies for the 1 and 0 bits
constexpr int START_FREQ = 7300;                        // Frequency of the beep to indicate start
constexpr int FINISH_FREQ = 7500;                       // Frequency of the beep to indicate end


static std::int16_t sinSample(double time, double freq, double amplitude) {
    return amplitude * std::sin(2 * PI * freq * time / SAMPLE_RATE) * 32767; // 32767 is max value of a 16 bit int
}

int main() {
    std::vector<std::int16_t> samples;

    constexpr int CHUNK_SIZE = 1024;        // 1kb

    std::ifstream file("path/to/file/to/encode", std::ios::binary);
    std::vector<char> fbuffer(CHUNK_SIZE);

    std::string encoded_data = "";

    for (int i = 0; i < SAMPLE_RATE * BIT_DURATION; i++) {
        samples.push_back(
            sinSample(i, START_FREQ, 0.5)
        );
    }

    while (file) {
        file.read(fbuffer.data(), CHUNK_SIZE);
        size_t bytesRead = file.gcount();


        for (int i = 0; i < bytesRead; i++) {
            // Operate on 1s and 0s
            for (int j = 7; j >= 0; j--) {
                bool bit = (fbuffer[i] >> j) & 1;                   // Extract bits sequentially

                encoded_data += bit ? "1" : "0";

                for (int k = 0; k < SAMPLE_RATE * BIT_DURATION; k++) {
                    // 1 is 1500Hz and 0 is 1000Hz
                    samples.push_back(
                        bit ? sinSample(k, TRUE_FREQ, 0.5) : sinSample(k, FALSE_FREQ, 0.5)
                    );
                }
            }
        }

        if (bytesRead < CHUNK_SIZE)
            break;
    }

    for (int i = 0; i < SAMPLE_RATE * BIT_DURATION; i++) {
        samples.push_back(
            sinSample(i, FINISH_FREQ, 0.5)
        );
    }


    sf::SoundBuffer buffer;

    if (!buffer.loadFromSamples(samples.data(), samples.size(), 1, SAMPLE_RATE)) {
        std::cerr << "Error while loading samples into buffer!\n";
    }
    
    sf::Sound sound(buffer);

	// Play the sound directly without writing to a file
    //sound.play();

    while (sound.getStatus() == sf::Sound::Playing) {
        sf::sleep(sf::milliseconds(100));
    }

    buffer.saveToFile("path/to/output/file");
	
    std::cout << "Encoded " << encoded_data.length() << " bits\n";
    std::cout << "Finished.\n";
}