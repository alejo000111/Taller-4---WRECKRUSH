shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled;

uniform float progreso = 0.0;
uniform float radio_interior = 0.0;
uniform float parpadeo = 0.0;
uniform vec4 naranja : source_color = vec4(1.0, 0.478, 0.102, 1.0);
uniform vec4 rojo : source_color = vec4(0.878, 0.227, 0.227, 1.0);

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float d = length(p);
	if (d > 1.0 || d < radio_interior) {
		discard;
	}
	float ancho = 0.05;
	float borde = step(1.0 - ancho, d);
	if (radio_interior > 0.001) {
		borde = max(borde, step(d, radio_interior + ancho));
	}
	float lleno = step(d, mix(radio_interior, 1.0, progreso));
	vec3 col = mix(naranja.rgb * 0.55, naranja.rgb, lleno);
	col = mix(col, rojo.rgb, borde);
	float a = mix(0.32, 0.78, lleno);
	a = max(a, borde * 0.95);
	ALBEDO = col;
	ALPHA = a * (0.7 + 0.3 * parpadeo);
}
