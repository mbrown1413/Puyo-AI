
#include <math.h>
#include <float.h>

static const int colors[6][3] = {  // HSV values (0-180, 0-255, 0-255)
    {120,  88,  40},  // Background
    {165, 154, 200},  // Red
    { 60, 242, 100},  // Green
    {105, 198, 140},  // Blue
    { 15, 110, 140},  // Yellow
    {135, 220, 120},  // Purple
};

static double color_dist(unsigned char h1, unsigned char s1, unsigned char v1,
                         unsigned char h2, unsigned char s2, unsigned char v2)
{
    //TODO: Circular distance for hue
    return sqrt( (h1-h2)*(h1-h2) + (s1-s2)*(s1-s2) + (v1-v2)*(v1-v2) );
}

/**
 * Takes a list of hsv pixels as a uint8 numpy array and outputs a list of
 * votes for how similar the pixels are to each color bean. The black
 * (nussance) bean is recognized as background.
 *
 * The BeanFinder class uses this to detect color.
 */
void get_color_votes(unsigned char* pixels,
                     int n_pixels,
                     int strides[2],
                     int votes_out[6])
{

    for(int i=0; i<6; i++) {
        votes_out[i] = 0;
    }

    // Each pixel votes for a color
    unsigned char* p = pixels;
    for(int i=0; i<n_pixels; i++) {
        unsigned char h = p[0*strides[1]];
        unsigned char s = p[1*strides[1]];
        unsigned char v = p[2*strides[1]];

        // Find the closest color to this pixel
        int closest_color = -1;
        double closest_dist = DBL_MAX;
        for(int j=0; j<6; j++) {
            double dist = color_dist(
                h, s, v,
                colors[j][0], colors[j][1], colors[j][2]);
            if(dist < closest_dist) {
                closest_dist = dist;
                closest_color = j;
            }
        }

        if(closest_color != -1 && closest_dist < 50) {
            votes_out[closest_color] += 1;
        }
        p += strides[0];
    }

}
