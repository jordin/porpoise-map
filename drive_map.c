#include <math.h>
#include <time.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

#define RANGE_MIN (300)
#define RANGE_MAX (1000)

#define ANGLE_MIN (0)
#define ANGLE_MAX (2 * M_PI)

#define RAND_DOUBLE ((double) rand() / RAND_MAX)

int main(void) {
    srand(time(NULL));
    while (1) {
        double range = RANGE_MIN + RAND_DOUBLE * (RANGE_MAX - RANGE_MIN);
        double angle = ANGLE_MIN + RAND_DOUBLE * (ANGLE_MAX - ANGLE_MIN);
        printf("0 %.3f %.3f\n", range, angle);
        sleep(1);
    }
}
