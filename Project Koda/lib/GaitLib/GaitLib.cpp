#include "GaitLib.h"
#include "GaitLookupTable.h"
#include <math.h>

// Lookup table now included from GaitLookupTable.h

// Helper: Euclidean distance
float pointDist(const Point& a, const Point& b) {
    return sqrtf((a.x - b.x)*(a.x - b.x) + (a.y - b.y)*(a.y - b.y));
}

// Generate curve points (simple examples, expand as needed)
int generateCurvePoints(CurveType type, const CurveParams& params, Point* outPoints, int maxPoints, CurveDirection direction) {
    int count = 0;
    if (type == VERTICAL) {
        for (float y = params.y0; y >= params.y0 - 80 && count < maxPoints; y -= 5.0) {
            outPoints[count++] = {params.x0, y};
        }
    } else if (type == LINE) {
        for (float x = params.x0; x <= params.x0 + 80 && count < maxPoints; x += 5.0) {
            float y = params.m * x + params.c;
            outPoints[count++] = {x, y};
        }
    } else if (type == HALF_FLAT_ELLIPSE) {
        // Arc-length stepping for half-flat-ellipse
        float xc = params.xc, yc = params.yc, a = params.a, b = params.b;
        float step_length_ellipse_mm = 2.5f;
        float step_length_flat_mm = 2.5f;
        const int n_fine = 1000;
        static float theta_fine[n_fine];
        static float x_fine[n_fine];
        static float y_fine[n_fine];
        static float s_ellipse[n_fine];
        if (direction == COUNTERCLOCKWISE) {
            // Top half-ellipse: theta from 0 to pi
            for (int i = 0; i < n_fine; ++i) {
                theta_fine[i] = (PI * i) / (n_fine - 1);
                x_fine[i] = xc + a * cos(theta_fine[i]);
                y_fine[i] = yc + b * sin(theta_fine[i]);
            }
        } else {
            // Top half-ellipse: theta from pi to 0
            for (int i = 0; i < n_fine; ++i) {
                theta_fine[i] = PI - (PI * i) / (n_fine - 1);
                x_fine[i] = xc + a * cos(theta_fine[i]);
                y_fine[i] = yc + b * sin(theta_fine[i]);
            }
        }
        s_ellipse[0] = 0.0f;
        for (int i = 1; i < n_fine; ++i) {
            float dx = x_fine[i] - x_fine[i-1];
            float dy = y_fine[i] - y_fine[i-1];
            s_ellipse[i] = s_ellipse[i-1] + sqrtf(dx*dx + dy*dy);
        }
        int n_steps_ellipse = (int)(s_ellipse[n_fine-1] / step_length_ellipse_mm);
        for (int k = 0; k <= n_steps_ellipse && count < maxPoints; ++k) {
            float s_target = (s_ellipse[n_fine-1] * k) / n_steps_ellipse;
            int idx = 0;
            while (idx < n_fine-1 && s_ellipse[idx] < s_target) ++idx;
            outPoints[count++] = {x_fine[idx], y_fine[idx]};
        }
        // Flat bottom
        float flat_y, x_start, x_end;
        if (direction == CLOCKWISE) {
            flat_y = y_fine[n_fine-1]; // right tip
            x_start = x_fine[0];      // left tip
            x_end = x_fine[n_fine-1]; // right tip
        } else {
            flat_y = y_fine[0];       // left tip
            x_start = x_fine[n_fine-1]; // right tip
            x_end = x_fine[0];        // left tip
        }
        float flat_length = fabsf(x_end - x_start);
        int n_steps_flat = (int)(flat_length / step_length_flat_mm);
        for (int k = 1; k < n_steps_flat && count < maxPoints-1; ++k) {
            float x_flat = x_start + (x_end - x_start) * k / n_steps_flat;
            outPoints[count++] = {x_flat, flat_y};
        }
        // Add endpoint to close the curve
        if (count < maxPoints) {
            outPoints[count++] = {x_end, flat_y};
        }
    }
    // ... add other curve types as needed ...
    return count;
}

// Match curve points to lookup table (greedy nearest neighbor, no reuse)
int matchCurveToLookup(const Point* curvePoints, int curveCount, const LookupEntry* lookupTable, int lookupCount, ServoAngles* outAngles, int maxAngles) {
    bool used[lookupCount] = {false};
    int outCount = 0;
    for (int i = 0; i < curveCount && outCount < maxAngles; ++i) {
        float minDist = 1e6;
        int minIdx = -1;
        for (int j = 0; j < lookupCount; ++j) {
            if (used[j]) continue;
            float d = pointDist(curvePoints[i], {lookupTable[j].x, lookupTable[j].y});
            if (d < minDist) {
                minDist = d;
                minIdx = j;
            }
        }
        if (minIdx >= 0) {
            outAngles[outCount++] = {lookupTable[minIdx].thetaA, lookupTable[minIdx].thetaD};
            used[minIdx] = true;
        }
    }
    return outCount;
}
