#version 450 core

in vec4 ourColor;
in float clipMe;
out vec4 FragColor;

void main() {
    if (clipMe > 0.5)
        discard;
    FragColor = ourColor;
}

