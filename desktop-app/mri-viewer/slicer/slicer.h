#pragma once
#include "../controls/controls.h"
#include "../tools/tools.h"
#include <GameEngine/Events/events.h>
#include <GameEngine/Graphics/camera.h>
#include <GameEngine/Graphics/renderer.h>

class Slicer {
    public:
        Slicer(std::string resourcePath, unsigned int nOfDivisions,
               Camera &camera);
        ~Slicer();
        void checkToolBar(ToolBar &tools);
        void render(Camera &camera);
        void handleEvent(Event &event, float deltaTime);
        int getNofSlices();
        void bindAllTextures();

    private:
        void clipSlice(int index);
        void initShaders(Camera &camera);
        void updateShader(int index, bool relevant[3][2]);
        bool checkRelevance(int index, int i, int j);
        void drawSlice(int i, int j);
        void renderVolume(Camera &camera, bool update);
        void renderSlices(Camera &camera, bool update);

        std::string path;
        int nOfSlices;
        int firstRelevantSlices[3][2];
        Controller controller;
        glm::mat4 model;
        glm::mat4 view;
        glm::mat4 projection;
        bool slicesRendered = true;
        bool cmapChanged;
        bool overlay = false;
        bool changed[3][2];
        float tresholds[3][2];
        int slicesIndices[3][2];
        int cmapIndex;
        Mesh *brainMesh;
        Actor brain;
        Shader *colorShader;
        Shader *textureShader;
        Mesh *slices[3][2];
        Texture *textures[6][2];
};
