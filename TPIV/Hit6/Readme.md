# Hit #6 - Shader Grayscale

## Objetivo

Agregar un filtro de escala de grises al resultado final del shader con chroma key.

## Implementación

Aplicamos la fórmula de luminancia perceptual recomendada por la Wikipedia (https://en.wikipedia.org/wiki/Grayscale):

```glsl
float gray = dot(color, vec3(0.2126, 0.7152, 0.0722));
color = vec3(gray);
```
