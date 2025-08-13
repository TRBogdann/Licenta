#version 450 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoord;

uniform float axis;
uniform float direction;
uniform float cmapIndex;
uniform sampler2D textureSampler;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec4 mxPoz;
uniform vec4 mnPoz;

out vec2 fragTexCoord;
out float clipMe;
out float fragCmap;

void main() {
   
    fragCmap = cmapIndex;
    clipMe = 0.0;
    if (position.x < mnPoz.x || position.x > mxPoz.x ||
        position.y < mnPoz.y || position.y > mxPoz.y ||
        position.z < mnPoz.z || position.z > mxPoz.z) {
        clipMe = 1.0;
    }
    
    float height = texture(textureSampler, texCoord).r;
    
    float aOffset =  0.1 - (1.0 - height) * 0.2;
    vec3 newPosition = position;
    
    if(axis < 0.1)
    {
        newPosition = newPosition + vec3(aOffset*direction,0.0,0.0);
    }
    else if(axis < 0.2)
    {
        newPosition = newPosition + vec3(0.0,aOffset*direction,0.0);
    }
    else
    {
        newPosition = newPosition + vec3(0.0,0.0,aOffset*direction);
    }
    gl_Position = projection * view * model * vec4(newPosition, 1.0);
    fragTexCoord = texCoord;
}

