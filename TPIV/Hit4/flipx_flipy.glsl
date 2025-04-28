void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord.xy / iResolution.xy;
    uv = 1.0 - uv;  
    fragColor = texture(iChannel0, uv);
}
