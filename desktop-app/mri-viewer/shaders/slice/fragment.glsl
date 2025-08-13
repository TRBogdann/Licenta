#version 450 core

in float fragCmap;
in float clipMe;
uniform float overlay;
uniform sampler2D textureSampler;
uniform sampler2D maskSampler;
in vec2 fragTexCoord;
out vec4 FragColor;


vec3 viridis(float x) {
    const vec3 c0 = vec3(0.267004, 0.004874, 0.329415);
    const vec3 c1 = vec3(0.229739, 0.322361, 0.545706);
    const vec3 c2 = vec3(0.127568, 0.566949, 0.550556);
    const vec3 c3 = vec3(0.369214, 0.788888, 0.382914);
    const vec3 c4 = vec3(0.993248, 0.906157, 0.143936);

    if (x < 0.25) return mix(c0, c1, x / 0.25);
    else if (x < 0.5) return mix(c1, c2, (x - 0.25) / 0.25);
    else if (x < 0.75) return mix(c2, c3, (x - 0.5) / 0.25);
    else return mix(c3, c4, (x - 0.75) / 0.25);
}

vec3 brainmap(float x) {
    vec3 c0 = vec3(0.35, 0.15, 0.25);
    vec3 c1 = vec3(0.75, 0.40, 0.50);  
    vec3 c2 = vec3(0.90, 0.65, 0.55);  
    vec3 c3 = vec3(0.98, 0.80, 0.65);  
    vec3 c4 = vec3(1.00, 0.90, 0.80);  
    if (x < 0.25) return mix(c0, c1, x / 0.25);
    else if (x < 0.5) return mix(c1, c2, (x - 0.25) / 0.25);
    else if (x < 0.75) return mix(c2, c3, (x - 0.5) / 0.25);
    else return mix(c3, c4, (x - 0.75) / 0.25);
}

vec3 inferno(float x) {
    const vec3 c0 = vec3(0.001462, 0.000466, 0.013866);
    const vec3 c1 = vec3(0.229739, 0.127568, 0.420886);
    const vec3 c2 = vec3(0.610467, 0.215601, 0.489690);
    const vec3 c3 = vec3(0.904156, 0.480978, 0.255757);
    const vec3 c4 = vec3(0.988362, 0.998364, 0.644924);

    if (x < 0.25) return mix(c0, c1, x / 0.25);
    else if (x < 0.5) return mix(c1, c2, (x - 0.25) / 0.25);
    else if (x < 0.75) return mix(c2, c3, (x - 0.5) / 0.25);
    else return mix(c3, c4, (x - 0.75) / 0.25);
}

vec3 magma(float x) {
    const vec3 c0 = vec3(0.001462, 0.000466, 0.013866);
    const vec3 c1 = vec3(0.251537, 0.116305, 0.342377);
    const vec3 c2 = vec3(0.478054, 0.220123, 0.460644);
    const vec3 c3 = vec3(0.781902, 0.419859, 0.404493);
    const vec3 c4 = vec3(0.987053, 0.991438, 0.749504);

    if (x < 0.25) return mix(c0, c1, x / 0.25);
    else if (x < 0.5) return mix(c1, c2, (x - 0.25) / 0.25);
    else if (x < 0.75) return mix(c2, c3, (x - 0.5) / 0.25);
    else return mix(c3, c4, (x - 0.75) / 0.25);
}

vec3 plasma(float x) {
    const vec3 c0 = vec3(0.050383, 0.029803, 0.527975);
    const vec3 c1 = vec3(0.415512, 0.033035, 0.611867);
    const vec3 c2 = vec3(0.733991, 0.215906, 0.506232);
    const vec3 c3 = vec3(0.969400, 0.518076, 0.223413);
    const vec3 c4 = vec3(0.940015, 0.975158, 0.131326);

    if (x < 0.25) return mix(c0, c1, x / 0.25);
    else if (x < 0.5) return mix(c1, c2, (x - 0.25) / 0.25);
    else if (x < 0.75) return mix(c2, c3, (x - 0.5) / 0.25);
    else return mix(c3, c4, (x - 0.75) / 0.25);
}

vec3 turbo(float x) {
    const vec3 c0 = vec3(0.18995, 0.07176, 0.23217);
    const vec3 c1 = vec3(0.26658, 0.35328, 0.68268);
    const vec3 c2 = vec3(0.47720, 0.77711, 0.40664);
    const vec3 c3 = vec3(0.99325, 0.90616, 0.14394);
    const vec3 c4 = vec3(0.97690, 0.98390, 0.08050);

    if (x < 0.25) return mix(c0, c1, x / 0.25);
    else if (x < 0.5) return mix(c1, c2, (x - 0.25) / 0.25);
    else if (x < 0.75) return mix(c2, c3, (x - 0.5) / 0.25);
    else return mix(c3, c4, (x - 0.75) / 0.25);
}

vec4 getcmap(vec4 inColor,float state)
{
   
    if(state <0.1)
    {
        vec3 newColor = brainmap(inColor.x);
        return vec4(newColor,inColor.w);
    }
    
    else if(state <0.2)
    {
        vec3 newColor = viridis(inColor.x);
        return vec4(newColor,inColor.w);

    }
    else if(state <0.3)
    {
        vec3 newColor = inferno(inColor.x);
        return vec4(newColor,inColor.w);

    }
    else if(state <0.4)
    {
        vec3 newColor = magma(inColor.x);
        return vec4(newColor,inColor.w);

    }
    else if(state <0.5)
    {
        vec3 newColor = plasma(inColor.x);
        return vec4(newColor,inColor.w);

    }
    else if(state <0.6)
    {
        vec3 newColor = turbo(inColor.x);
        return vec4(newColor,inColor.w);

    }
    else{
        return inColor;
    }
}


vec4 get_final_color(vec4 pixel,vec4 mask,float state)
{
    if(mask.w < 0.5f)
        return pixel;

    vec4 c1 = vec4(1.0,0.0,0.0,1.0);
    vec4 c2 = vec4(0.0,1.0,0.0,1.0);
    vec4 c3 = vec4(0.0,0.0,1.0,1.0);
    
    if(state >= 0.1 && state < 0.6)
    {
        if(state < 0.2)
        {
            c2 = vec4(1.0,0.0,1.0,1.0);
            c3 = vec4(1.0,1.0,1.0,1.0);
        }
        else if(state < 0.5)
        {
            c1 = vec4(0.0,1.0,1.0,1.0);
            c3 = vec4(1.0,1.0,1.0,1.0);
        }
        else
        {
            c1 = vec4(0.0,0.0,0.0,1.0);
            c2 = vec4(1.0,1.0,1.0,1.0);
            c3 = vec4(0.0,1.0,1.0,1.0);
        }
    }
    
    if(mask.x > 0.0)
    {
          return c1;
    }
    else if(mask.y > 0.0)
    {
        return c2;
    }
    else if(mask.z > 0.0)
    {
        return c3;
    }
    else
    {
        return pixel;
    }
}

void main() {
    if (clipMe > 0.5)
        discard;

    vec4 texColor = texture(textureSampler, fragTexCoord);
    vec4 maskColor = texture(maskSampler, fragTexCoord);
    vec4 mapColor = getcmap(texColor,fragCmap);
    
    if(overlay>0.5)
    {
        vec4 finalColor = get_final_color(mapColor,maskColor,fragCmap);
        FragColor = finalColor;
    }
    else
    {
        FragColor = mapColor;
    }
}
