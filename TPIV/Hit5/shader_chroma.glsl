void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord.xy / iResolution.xy;

    vec4 foreground = texture(iChannel1, uv);
    vec4 background = texture(iChannel0, uv);

    vec3 chromaColor = vec3(0.1, 1.0, 0.1);
    float threshold = 0.6;
    float slope = 0.1;

    float d = distance(foreground.rgb, chromaColor); 
    float alpha = smoothstep(threshold - slope, threshold + slope, d);

    vec3 color = mix(background.rgb, foreground.rgb, alpha);
    fragColor = vec4(color, 1.0);
}
