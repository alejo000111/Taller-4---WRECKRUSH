shader_type spatial;
render_mode unshaded, depth_test_disabled, cull_disabled, blend_mix;

uniform float proporcion = 1.0;
uniform vec4 relleno : source_color = vec4(0.878, 0.227, 0.227, 1.0);
uniform vec4 fondo : source_color = vec4(0.08, 0.09, 0.1, 0.85);

void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
}

void fragment() {
	float lleno = step(UV.x, proporcion);
	float margen = step(0.12, UV.y) * step(UV.y, 0.88) * step(0.02, UV.x) * step(UV.x, 0.98);
	vec4 c = mix(fondo, relleno, lleno * margen);
	ALBEDO = c.rgb;
	ALPHA = c.a;
}
