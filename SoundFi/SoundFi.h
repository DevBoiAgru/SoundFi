#pragma once

#include <iostream>
#include <SFML/Audio.hpp>
#include <cmath>
#include <fstream>

static std::int16_t sinSample(double time, double freq, double amplitude);

// Pushes samples for a beep of a given frequency and amplitude equal to specified length (seconds) 
// at the provided sample rate
static void generate_beep(std::vector<std::int16_t>& sample_array, float frequency, float amplitude, float length, int sample_rate);