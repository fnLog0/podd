#pragma once

#include "../app/ApplicationState.h"

void setupWiFi();
bool connectWiFi();
void maintainWiFiConnection(AppState& state);
