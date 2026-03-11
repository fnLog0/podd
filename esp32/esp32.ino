#include "src/core/AppController.h"
#include "src/core/AppState.h"

AppState appState;

void setup() {
  setupApp(appState);
}

void loop() {
  loopApp(appState);
}
