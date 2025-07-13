#ifndef GAITLIB_H
#define GAITLIB_H

#include <Arduino.h>

struct Point {
    float x;
    float y;
};

struct ServoAngles {
    int thetaA;
    int thetaD;
};

// Example lookup table entry
struct LookupEntry {
    int thetaA;
    int thetaD;
    float x;
    float y;
};

// Curve types
enum CurveType {
    VERTICAL,
    HORIZONTAL,
    LINE,
    CIRCLE,
    ELLIPSE,
    HALF_FLAT_ELLIPSE
};

struct CurveParams {
    // Only fill the relevant fields for your curve type
    float x0, y0, m, c, xc, yc, r, a, b;
};

// Direction for curve generation: +1 for CCW, -1 for CW
// Use sign of direction argument for all curve types
int generateCurvePoints(CurveType type, const CurveParams& params, Point* outPoints, int maxPoints, int direction = 1);

// Match curve points to lookup table
int matchCurveToLookup(const Point* curvePoints, int curveCount, const LookupEntry* lookupTable, int lookupCount, ServoAngles* outAngles, int maxAngles);

#endif // GAITLIB_H
