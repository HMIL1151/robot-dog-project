#include "GaitLib.h"
#include "GaitLookupTable.h"
#include <math.h>

// Lookup table now included from GaitLookupTable.h

// Helper: Euclidean distance
float pointDist(const Point& a, const Point& b) {
    return sqrtf((a.x - b.x)*(a.x - b.x) + (a.y - b.y)*(a.y - b.y));
}

// Generate curve points (simple examples, expand as needed)
int generateCurvePoints(CurveType type, const CurveParams& params, Point* outPoints, int maxPoints, int direction) {
    int count = 0;
    if (type == VERTICAL) {
        // Vertical line: x = x0, y from y_min to y_max
        float step = 5.0f * (direction >= 0 ? 1 : -1);
        float y_start = (direction >= 0) ? params.y0 : params.yc;
        float y_end   = (direction >= 0) ? params.yc : params.y0;
        if (step > 0) {
            for (float y = y_start; y <= y_end && count < maxPoints; y += step) {
                outPoints[count++] = {params.x0, y};
            }
        } else {
            for (float y = y_start; y >= y_end && count < maxPoints; y += step) {
                outPoints[count++] = {params.x0, y};
            }
        }
    } else if (type == HORIZONTAL) {
        // Horizontal line: y = y0, x from x_min to x_max
        float step = 5.0f * (direction >= 0 ? 1 : -1);
        float x_start = (direction >= 0) ? params.x0 : params.xc;
        float x_end   = (direction >= 0) ? params.xc : params.x0;
        if (step > 0) {
            for (float x = x_start; x <= x_end && count < maxPoints; x += step) {
                outPoints[count++] = {x, params.y0};
            }
        } else {
            for (float x = x_start; x >= x_end && count < maxPoints; x += step) {
                outPoints[count++] = {x, params.y0};
            }
        }
    } else if (type == LINE) {
        // Straight line: y = m*x + c, x from x_min to x_max
        float step = 5.0f * (direction >= 0 ? 1 : -1);
        float x_start = (direction >= 0) ? params.x0 : params.xc;
        float x_end   = (direction >= 0) ? params.xc : params.x0;
        if (step > 0) {
            for (float x = x_start; x <= x_end && count < maxPoints; x += step) {
                float y = params.m * x + params.c;
                outPoints[count++] = {x, y};
            }
        } else {
            for (float x = x_start; x >= x_end && count < maxPoints; x += step) {
                float y = params.m * x + params.c;
                outPoints[count++] = {x, y};
            }
        }
    } else if (type == ELLIPSE) {
        // Ellipse: (x-xc)^2/a^2 + (y-yc)^2/b^2 = 1
        float xc = params.xc, yc = params.yc, a = params.a, b = params.b;
        float step_length_ellipse_mm = 5.0f;
        const int n_fine = 1000;
        static float theta_fine[n_fine];
        static float x_fine[n_fine];
        static float y_fine[n_fine];
        static float s_ellipse[n_fine];
        float theta_start = (direction >= 0) ? 0.0f : 2*PI;
        float theta_end   = (direction >= 0) ? 2*PI : 0.0f;
        for (int i = 0; i < n_fine; ++i) {
            float t = (float)i / (n_fine - 1);
            theta_fine[i] = theta_start + (theta_end - theta_start) * t;
            x_fine[i] = xc + a * cos(theta_fine[i]);
            y_fine[i] = yc + b * sin(theta_fine[i]);
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
        float theta_start = (direction >= 0) ? 0.0f : PI;
        float theta_end   = (direction >= 0) ? PI : 0.0f;
        for (int i = 0; i < n_fine; ++i) {
            float t = (float)i / (n_fine - 1);
            theta_fine[i] = theta_start + (theta_end - theta_start) * t;
            x_fine[i] = xc + a * cos(theta_fine[i]);
            y_fine[i] = yc + b * sin(theta_fine[i]);
        }
        s_ellipse[0] = 0.0f;
        for (int i = 1; i < n_fine; ++i) {
            float dx = x_fine[i] - x_fine[i-1];
            float dy = y_fine[i] - y_fine[i-1];
            s_ellipse[i] = s_ellipse[i-1] + sqrtf(dx*dx + dy*dy);
        }
        int n_steps_ellipse = (int)(s_ellipse[n_fine-1] / step_length_ellipse_mm);
        float flat_y, x_start, x_end;
        if (direction >= 0) {
            // Positive direction: ellipse then line
            for (int k = 0; k <= n_steps_ellipse && count < maxPoints; ++k) {
                float s_target = (s_ellipse[n_fine-1] * k) / n_steps_ellipse;
                int idx = 0;
                while (idx < n_fine-1 && s_ellipse[idx] < s_target) ++idx;
                outPoints[count++] = {x_fine[idx], y_fine[idx]};
            }
            flat_y = y_fine[n_fine-1]; // right tip (end of ellipse)
            x_start = x_fine[n_fine-1]; // right tip (start of flat)
            x_end = x_fine[0];          // left tip (end of flat)
            float flat_length = fabsf(x_end - x_start);
            int n_steps_flat = (int)(flat_length / step_length_flat_mm);
            for (int k = 1; k < n_steps_flat && count < maxPoints-1; ++k) {
                float x_flat = x_start + (x_end - x_start) * k / n_steps_flat;
                outPoints[count++] = {x_flat, flat_y};
            }
            if (count < maxPoints) {
                outPoints[count++] = {x_end, flat_y};
            }
        } else {
            // Negative direction: line then ellipse
            flat_y = y_fine[0];        // left tip (start of ellipse)
            x_start = x_fine[n_fine-1]; // right tip (start of flat)
            x_end = x_fine[0];         // left tip (end of flat)
            float flat_length = fabsf(x_end - x_start);
            int n_steps_flat = (int)(flat_length / step_length_flat_mm);
            for (int k = 1; k < n_steps_flat && count < maxPoints-1; ++k) {
                float x_flat = x_start + (x_end - x_start) * k / n_steps_flat;
                outPoints[count++] = {x_flat, flat_y};
            }
            if (count < maxPoints) {
                outPoints[count++] = {x_end, flat_y};
            }
            for (int k = 0; k <= n_steps_ellipse && count < maxPoints; ++k) {
                float s_target = (s_ellipse[n_fine-1] * k) / n_steps_ellipse;
                int idx = 0;
                while (idx < n_fine-1 && s_ellipse[idx] < s_target) ++idx;
                outPoints[count++] = {x_fine[idx], y_fine[idx]};
            }
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
