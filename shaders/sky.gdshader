shader_type sky;

uniform samplerCube cielo : source_color, filter_linear;
uniform vec4 tinte : source_color = vec4(1.0);
uniform float energia = 1.0;

void sky() {
	COLOR = texture(cielo, EYEDIR).rgb * tinte.rgb * energia;
}
