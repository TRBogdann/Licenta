#include "slicer.h"
#include <GameEngine/Events/events.h>
#include <GameEngine/Files/files.h>
#include <GameEngine/Graphics/graphics.h>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>

std::string numberToFile(int number) {
    std::ostringstream ss;
    ss << "slice_" << std::setw(3) << std::setfill('0') << number << ".png";
    return ss.str();
}

void Slicer::initShaders(Camera &camera) {

    model = glm::mat4(1.0f);
    model = glm::translate(model, brain.getPosition());
    model = model * Transform::rotation(brain.getRotation());
    model = glm::scale(model, brain.getScale());
    view = camera.getView();
    projection = camera.getProjection(Program_Settings::aspectRatio);

    this->textureShader->bind();
    this->textureShader->setUniform1f("axis", 0.0f);
    this->textureShader->setUniform1f("direction", 1.0f);
    this->textureShader->setUniform1f("cmapIndex", 0.0f);
    this->textureShader->setUniform4f("mnPoz", -1.0f, -1.0f, -1.0f, 0.0f);
    this->textureShader->setUniform4f("mxPoz", 1.0f, 1.0f, 1.0f, 0.0f);
    this->textureShader->setUniformMat4("model", model);
    this->textureShader->setUniformMat4("view", view);
    this->textureShader->setUniformMat4("projection", projection);

    this->colorShader->bind();
    this->colorShader->setUniform1f("cmapIndex", 0.0f);
    this->colorShader->setUniform4f("mnPoz", -1.0f, -1.0f, -1.0f, 0.0f);
    this->colorShader->setUniform4f("mxPoz", 1.0f, 1.0f, 1.0f, 0.0f);
    this->colorShader->setUniformMat4("model", model);
    this->colorShader->setUniformMat4("view", view);
    this->colorShader->setUniformMat4("projection", projection);
}

Slicer::Slicer(std::string resourcePath, unsigned int nOfDivisions,
               Camera &camera)
    : controller(Controller(20.0f, 5.0f)),
      cmapIndex(0),
      brain({0.0f, 0.0f, 50.0f}, {10.0f, 10.f, 10.f}) {
    std::ifstream config(resourcePath + "/slicer.config");
    config >> nOfSlices;
    for (int i = 0; i < 3; i++) {

        // TODO
        // config >> this->firstRelevantSlices[i][0];
        // config >> this->firstRelevantSlices[i][1];

        this->firstRelevantSlices[i][0] = 0;
        this->firstRelevantSlices[i][1] = nOfSlices - 1;

        this->changed[i][0] = false;
        this->changed[i][0] = false;

        this->slicesIndices[i][0] = 0;
        this->slicesIndices[i][1] = nOfSlices - 1;

        this->tresholds[i][0] = -1.0f;
        this->tresholds[i][1] = 1.0f;
    }

    this->path = resourcePath;
    this->cmapIndex = 0;
    this->cmapChanged = false;

    std::ifstream vertexBrainFile(resourcePath + "/shaders/brain/vertex.glsl");
    std::ifstream fragmentBrainFile(resourcePath +
                                    "/shaders/brain/fragment.glsl");
    std::string vertexBrainShader = FileToString(vertexBrainFile);
    std::string fragmentBrainShader = FileToString(fragmentBrainFile);

    std::ifstream vertexSliceFile(resourcePath + "/shaders/slice/vertex.glsl");
    std::ifstream fragmentSliceFile(resourcePath +
                                    "/shaders/slice/fragment.glsl");
    std::string vertexSliceShader = FileToString(vertexSliceFile);
    std::string fragmentSliceShader = FileToString(fragmentSliceFile);

    this->colorShader = new Shader(vertexBrainShader, fragmentBrainShader);
    this->textureShader = new Shader(vertexSliceShader, fragmentSliceShader);

    GraphicalAtribute *atributes =
        GraphicalAtribute::getCreator()->createAtributes(SHADER_COLOR,
                                                         COORDINATES_XYZ);
    unsigned int nOfAtributes =
        GraphicalAtribute::getCreator()->getNOfAtributes();

    this->brainMesh =
        Mesh::loadMesh(resourcePath + "/brain.obj", ENGINE_SIMPLE_FILE_FORMAT,
                       colorShader, nOfAtributes, atributes);

    delete[] atributes;

    atributes = GraphicalAtribute::getCreator()->createAtributes(
        SHADER_TEXTURE, COORDINATES_XYZ);
    nOfAtributes = GraphicalAtribute::getCreator()->getNOfAtributes();

    Mesh *tempMesh = Surface::generateFlatConstantSurface(
        nOfDivisions, nOfDivisions, textureShader, SHADER_TEXTURE, true);

    for (int i = 0; i < 3; i++) {
        slices[i][0] =
            new Mesh(tempMesh->Data(), tempMesh->getDataSize(),
                     this->textureShader, nOfAtributes, atributes, true);
    }
    Model::rotate(slices[2][0], 5, {1.0f, 0.0f, 0.0f}, 90.0f);
    Model::rotate(slices[1][0], 5, {1.0f, 0.0f, 0.0f}, 180.0f);
    Model::rotate(slices[0][0], 5, {1.0f, 0.0f, 0.0f}, 180.0f, false);
    Model::rotate(slices[0][0], 5, {0.0f, 0.0f, 1.0f}, 90.f);

    for (int i = 0; i < 3; i++) {
        slices[i][1] =
            new Mesh(slices[i][0]->Data(), slices[i][0]->getDataSize(),
                     this->textureShader, nOfAtributes, atributes, true);
    }

    for (int i = 0; i < 6; i++) {
        textures[i][0] = nullptr;
        textures[i][1] = nullptr;
    }

    initShaders(camera);
    glDisable(GL_CULL_FACE);
    glDepthFunc(GL_LEQUAL);

    delete tempMesh;
    delete[] atributes;
}

int Slicer::getNofSlices() { return this->nOfSlices; }

Slicer::~Slicer() {

    delete colorShader;
    delete textureShader;
    delete brainMesh;
    for (int i = 0; i < 3; i++) {
        delete slices[i][0];
        delete slices[i][1];
    }
    for (int i = 0; i < 6; i++) {
        if (textures[i][0])
            delete textures[i][0];
        if (textures[i][1])
            delete textures[i][1];
    }
}

bool Slicer::checkRelevance(int index, int i, int j) {

    bool check1 = (index > 0) && (index < nOfSlices - 1);
    bool check2 = (index >= this->firstRelevantSlices[i][0]) &&
                  (index <= this->firstRelevantSlices[i][1]);

    bool check3 = (j == 1) || (index < this->slicesIndices[i][1]);
    bool check4 = (j == 0) || (index > this->slicesIndices[i][0]);

    return check1 && check2 && check3 && check4;
}

void Slicer::checkToolBar(ToolBar &tools) {

    this->overlay = tools.overlay;

    if (this->cmapIndex != tools.getCurrentMap()) {
        this->cmapIndex = tools.getCurrentMap();
        this->cmapChanged = true;
    }

    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 2; j++) {
            int index = tools.getSliceIndex(i, j);
            if (this->slicesIndices[i][j] != index) {
                this->slicesIndices[i][j] = index;
                this->changed[i][j] = true;
                this->tresholds[i][j] =
                    -1.0f + (2.0f * index) / (nOfSlices - 1.0f);
                if (checkRelevance(index, i, j)) {
                    if (textures[2 * i + j][0] != nullptr) {
                        delete textures[2 * i + j][0];
                    }
                    if (textures[2 * i + j][1] != nullptr) {
                        delete textures[2 * i + j][1];
                    }
                    std::string num =
                        std::to_string(2 - i) + "/" + numberToFile(index);
                    std::string slicePath = this->path + "/slices/axis_" + num;
                    std::string maskPath = this->path + "/masks/axis_" + num;

                    this->textures[2 * i + j][0] = new Texture(slicePath, 0, 1);
                    this->textures[2 * i + j][0]->bind(2 * i + j);
                    this->textures[2 * i + j][1] = new Texture(maskPath, 0, 1);
                    this->textures[2 * i + j][1]->bind(6 + 2 * i + j);

                    Model::modifyAxis(this->slices[i][j], this->tresholds[i][j],
                                      i, 5);
                }
            }
        }
}

void Slicer::handleEvent(Event &event, float deltaTime) {
    this->controller.handleEventFor(brain, event, deltaTime);
}
void Slicer::renderVolume(Camera &camera, bool update) {
    if (slicesRendered) {
        colorShader->bind();
    }
    if (cmapChanged) {
        colorShader->setUniform1f("cmapIndex", 0.1f * this->cmapIndex);
    }

    if (update) {
        colorShader->setUniform4f("mnPoz", this->tresholds[0][0],
                                  this->tresholds[1][0], this->tresholds[2][0],
                                  0.0f);

        colorShader->setUniform4f("mxPoz", this->tresholds[0][1],
                                  this->tresholds[1][1], this->tresholds[2][1],
                                  0.0f);
    }

    if (this->controller.handled) {

        model = glm::mat4(1.0f);
        model = glm::translate(model, brain.getPosition());
        model = model * Transform::rotation(brain.getRotation());
        model = glm::scale(model, brain.getScale());
        view = camera.getView();
        projection = camera.getProjection(Program_Settings::aspectRatio);

        colorShader->setUniformMat4("model", model);
        colorShader->setUniformMat4("view", view);
        colorShader->setUniformMat4("projection", projection);
    }

    brainMesh->getVertexArray()->bind();
    glDrawArrays(GL_TRIANGLES, 0, brainMesh->getVertexCount());
}

void Slicer::updateShader(int index, bool relevant[3][2]) {
    float minVal[3];
    float maxVal[3];

    for (int i = 0; i < 3; i++) {
        if (i == index) {
            minVal[i] = -1.0f;
            maxVal[i] = 1.0f;
        } else {
            minVal[i] = this->tresholds[i][0];
            maxVal[i] = this->tresholds[i][1];
        }
    }

    textureShader->setUniform4f("mnPoz", minVal[0], minVal[1], minVal[2], 0.0f);
    textureShader->setUniform4f("mxPoz", maxVal[0], maxVal[1], maxVal[2], 0.0f);
    textureShader->setUniform1f("axis", 0.1f * index);
}

void Slicer::bindAllTextures() {
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 2; j++) {
            if (textures[2 * i + j][0]) {
                textures[2 * i + j][0]->bind(2 * i + j);
            }

            if (textures[2 * i + j][1]) {
                textures[2 * i + j][1]->bind(6 + 2 * i + j);
            }
        }
    }
}

void Slicer::drawSlice(int i, int j) {
    textureShader->setUniform1i("textureSampler", 2 * i + j);
    textureShader->setUniform1i("maskSampler", 6 + 2 * i + j);
    textureShader->setUniform1f("axis", 0.1f * i);
    textureShader->setUniform1f("direction", j == 0 ? -1.0f : 1.0f);
    this->slices[i][j]->getVertexArray()->bind();
    glDrawArrays(GL_TRIANGLES, 0, this->slices[i][j]->getVertexCount());
}

void Slicer::clipSlice(int index) {
    float mnPoz[3];
    float mxPoz[3];

    for (int i = 0; i < 3; i++) {
        if (i == index) {
            mnPoz[i] = -1.0f;
            mxPoz[i] = 1.0f;
        } else {
            mnPoz[i] = this->tresholds[i][0];
            mxPoz[i] = this->tresholds[i][1];
        }
    }

    this->textureShader->setUniform4f("mnPoz", mnPoz[0], mnPoz[1], mnPoz[2],
                                      1.0f);
    this->textureShader->setUniform4f("mxPoz", mxPoz[0], mxPoz[1], mxPoz[2],
                                      1.0f);
}

void Slicer::renderSlices(Camera &camera, bool update) {

    this->textureShader->bind();
    this->textureShader->setUniform1f("overlay", this->overlay ? 1.0 : 0.0);
    if (update) {
        bindAllTextures();
    }

    if (update) {
        textureShader->setUniformMat4("model", model);
        textureShader->setUniformMat4("view", view);
        textureShader->setUniformMat4("projection", projection);
    }

    if (cmapChanged) {
        textureShader->setUniform1f("cmapIndex", 0.1f * this->cmapIndex);
    }

    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 2; j++)
            if (textures[2 * i + j][0] &&
                checkRelevance(this->slicesIndices[i][j], i, j) &&
                textures[6 + 2 * i + j]) {
                clipSlice(i);
                drawSlice(i, j);
            }
}

void Slicer::render(Camera &camera) {

    bool update = false;
    for (int i = 0; i < 3; i++) {
        update = update || this->changed[i][0] || this->changed[i][1];
    }

    this->colorShader->bind();
    this->renderVolume(camera, update);
    this->renderSlices(camera, update);
}
