import manim
from manim import *
import math

config.background_color = "#020B15"

thighLength = 30
calfLength = 105
servoDistance = 46
hipSeperation = 160
servoAxisDistance = 31.56
footZ = 10
footY = 120
footX = 0

arcRadii = 10


divisor = 26

def convertDistance(value):
    return value / divisor

def createRelativePoint(robotOrigin:Dot, x, y):
        xDisplay = convertDistance(x)
        yDisplay = convertDistance(y)

        origin = robotOrigin.get_center()

        originX = origin[0]
        originY = origin[1]

        return Dot(point=[originX - xDisplay, originY - yDisplay, 0])

def getAllIntersectionPoints(footX, footY, servoCentre) -> list[Dot]:
    foot_coords = (footX, footY)
    servo1_coords = (-servoDistance/2, 0)
    servo2_coords = (servoDistance/2, 0)

    foot_circle = (foot_coords, calfLength)
    thigh_circle_1 = (servo1_coords, thighLength)
    thigh_circle_2 = (servo2_coords, thighLength)

    def intersection_between_circles(circle1, circle2):
        # Unpack circle1 and circle2
        ((x1, y1), r1) = circle1
        ((x2, y2), r2) = circle2

        # Calculate the distance between the centers
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))

        intersection_coords = []

        # Check if circles intersect
        if distance < r1 + r2 and distance > 0:
            # Calculate intersection points (simplified)

            a = (math.pow(r1, 2) - math.pow(r2, 2) + math.pow(distance, 2)) / (2 * distance)
            if (math.pow(r1, 2) - math.pow(a, 2)) < 0:
                return intersection_coords
            h = math.sqrt(math.pow(r1, 2) - math.pow(a, 2))
            x5 = x1 + a/distance * dx
            y5 = y1 + a/distance * dy

            x3 = x5 - h/distance * dy
            y3 = y5 + h/distance * dx
            intersection_coords.append((x3, y3))

            x4 = x5 + h/distance * dy
            y4 = y5 - h/distance * dx
            intersection_coords.append((x4, y4))

        return intersection_coords

    def clockwise_angle_between_two_lines(point1, point2, intersection_point):

        x1, y1 = point1
        x2, y2 = point2
        xi, yi = intersection_point

        v1x, v1y = x1 - xi, y1 - yi
        v2x, v2y = x2 - xi, y2 - yi

        theta1 = math.atan2(v1y, v1x)
        theta2 = math.atan2(v2y, v2x)

        delta_cw = theta1 - theta2
        delta_cw = (delta_cw + 2 * math.pi) % (2 * math.pi)
        return math.degrees(delta_cw)

        

    servo1_intersection_coords = intersection_between_circles(foot_circle, thigh_circle_1)
    servo2_intersection_coords = intersection_between_circles(foot_circle, thigh_circle_2)

    if servo1_intersection_coords and servo2_intersection_coords:

        servo1_intersection_angles = (
            clockwise_angle_between_two_lines(servo1_coords, foot_coords, servo1_intersection_coords[0]),
            clockwise_angle_between_two_lines(servo1_coords, foot_coords, servo1_intersection_coords[1])
        )
        servo2_intersection_angles = (
            clockwise_angle_between_two_lines(servo2_coords, foot_coords, servo2_intersection_coords[0]),
            clockwise_angle_between_two_lines(servo2_coords, foot_coords, servo2_intersection_coords[1])
        )

        if servo1_intersection_angles[0] < 180:
            leftServoIntersectionPoint = servo1_intersection_coords[1]
        else:
            leftServoIntersectionPoint = servo1_intersection_coords[0]

        if servo2_intersection_angles[0] < 180:
            rightServoIntersectionPoint = servo2_intersection_coords[0]
        else:
            rightServoIntersectionPoint = servo2_intersection_coords[1]

    else:
        raise ValueError("No Intersection Points")
    
    rawIntersectionPoints = servo1_intersection_coords + servo2_intersection_coords
    intersectionPoints = []
    for i in range(4):
        intersectionPoints.append(
            Dot(color=YELLOW)
            .move_to(servoCentre + RIGHT * convertDistance(rawIntersectionPoints[i][0]) + DOWN * convertDistance(rawIntersectionPoints[i][1]))
            .set_z_index(100)
        )
    
        
    return intersectionPoints

def getDimensionArrowFromLine(
    line: Line,
    offset: float = 0.4,
    buff: float = 0.0,
    stroke=3,
    tip_shape=StealthTip,
    max_tip_length_to_length_ratio=0.05,
    label=None,  # LaTeX label
    label_offset: float = 0.3,  # Offset for label normal to arrow
    label_kwargs=None,
    **arrow_kwargs
) -> VGroup:
    start = line.get_start()
    end = line.get_end()

    v = end - start
    length = np.linalg.norm(v)

    if length == 0:
        raise ValueError("Cannot create dimension arrow for zero-length line.")

    # Unit perpendicular vector
    v_unit = v / length
    perp = np.array([-v_unit[1], v_unit[0], 0])

    offset_vec = offset * perp

    arrow = DoubleArrow(
        start + offset_vec,
        end + offset_vec,
        buff=buff,
        tip_shape=tip_shape,
        tip_shape_start=tip_shape,
        stroke_width=stroke,
        max_tip_length_to_length_ratio=max_tip_length_to_length_ratio,
        **arrow_kwargs,
    )

    if label is not None:
        label_kwargs = label_kwargs or {}
        label_mobj = MathTex(label, **label_kwargs)
        # Position label at center of arrow, offset further along perp
        label_mobj.move_to(arrow.get_center() + label_offset * perp)
        return VGroup(arrow, label_mobj)
    else:
        return arrow



class HipAxisView(Scene):
    def construct(self):
        legOrigin = Dot(point=manim.ORIGIN + UP * 3, color=BLUE)

        foot = createRelativePoint(legOrigin, footZ, footY)
        servoCentre = createRelativePoint(legOrigin, hipSeperation/2, 0)

        q = convertDistance(hipSeperation/2 - footZ)
        a = convertDistance(servoAxisDistance)
        b = math.sqrt(math.pow(q,2) + math.pow(convertDistance(footY), 2) - math.pow(a,2))
        print("b: " + str(b))

        hipAngle1 = math.atan(convertDistance(footY)/q)
        hipAngle2 = math.atan(b/a) 
        hipAngle = hipAngle1 + hipAngle2
        print("hip angle: " + str(hipAngle))

        knee = createRelativePoint(servoCentre, servoAxisDistance * math.sin(hipAngle - math.pi/2), servoAxisDistance * math.cos(hipAngle - math.pi/2))

        leg = Line(knee.get_center(), foot.get_center())
        servoShaft = Line(servoCentre.get_center(), knee.get_center())

        legArrow = getDimensionArrowFromLine(leg, color=RED, offset=-0.4)
        legArrowLabel = MathTex('b', color=RED).move_to(legArrow.get_midpoint() + LEFT*0.2 + DOWN*0.2)
        servoShaftArrow = getDimensionArrowFromLine(servoShaft, offset=-0.2, stroke_color=LIGHT_PINK)
        servoShaftLabel = MathTex('a', color=LIGHT_PINK).move_to(servoShaftArrow.get_midpoint() + UP*0.4)
        yDashedLine = DashedLine(foot.get_center(), [foot.get_center()[0], legOrigin.get_center()[1], 0])
        zDashedLine = DashedLine(foot.get_center(), [legOrigin.get_center()[0], foot.get_center()[1], 0])

        hipSeperationDashedLine = DashedLine(servoCentre.get_center(), legOrigin.get_center())
        hipSeperationArrow = getDimensionArrowFromLine(hipSeperationDashedLine, offset=0.2)
        hipSeperationLabel = MathTex('d/2').move_to(hipSeperationArrow.get_midpoint() + UP*0.3 + RIGHT*0.2)

        qLine = Line(servoCentre.get_center(), [foot.get_center()[0], legOrigin.get_center()[1], 0])
        qArrow = getDimensionArrowFromLine(qLine, offset=0.2, stroke_color=YELLOW)
        qLineLabel = MathTex('q', color=YELLOW).next_to(qArrow, UP*0.4)
        
        yArrow = getDimensionArrowFromLine(yDashedLine, offset=-0.4, stroke_color=MAROON_A)
        yLabel = MathTex('y', color=MAROON_A).next_to(yArrow, RIGHT*0.4)
        zArrow = getDimensionArrowFromLine(zDashedLine, offset=0.2, stroke_color=TEAL).shift(UP * convertDistance(footY))
        zLabel = MathTex('z', color=TEAL).next_to(zArrow, UP*0.4)

        fLine = DashedLine(foot.get_center(), servoCentre.get_center())
        fLineMidpoint = (foot.get_center() + servoCentre.get_center()) / 2
        fLineLabel = MathTex('f', color=GOLD).move_to(fLineMidpoint + RIGHT*0.2 + UP*0.6)

        angleArcRadii = convertDistance(arcRadii)
        hipAngleArc = Angle(hipSeperationDashedLine, 
                            servoShaft, radius=angleArcRadii, color=WHITE, quadrant=(1, 1), other_angle=True)
        hipAngleSector = Sector(
                    arc_center=servoCentre.get_center(),  # or the correct center
                    radius=angleArcRadii,
                    start_angle=0,           # in radians
                    angle=-hipAngle,                     # in radians
                    fill_color=GRAY,
                    fill_opacity=0.7,
                    stroke_width=0
                ) 
        hipAngleLabel = MathTex(r'\theta_h').move_to(hipAngleSector.get_center()).scale(0.6)
        hipAngle1Arc = Angle(hipSeperationDashedLine, fLine, radius=angleArcRadii, color=ORANGE, quadrant=(1, -1), other_angle=True)
        hipAngle1Sector = Sector(
                    arc_center=servoCentre.get_center(),  # or the correct center
                    radius=angleArcRadii,
                    start_angle=0,           # in radians
                    angle=-hipAngle1,                     # in radians
                    fill_color=ORANGE,
                    fill_opacity=0.7,
                    stroke_width=0
                )
        hipAngle2Arc = Angle(fLine, servoShaft, radius=angleArcRadii, color=GREEN, quadrant=(-1, 1), other_angle=True)
        hipAngle2Sector = Sector(
                    arc_center=servoCentre.get_center(),  # or the correct center
                    radius=angleArcRadii,
                    start_angle=-hipAngle1,           # in radians
                    angle=-hipAngle2,                     # in radians
                    fill_color=GREEN,
                    fill_opacity=0.7,
                    stroke_width=0
                )


        legServoSquareAngle = RightAngle(leg, servoShaft, length=angleArcRadii, color=WHITE, quadrant=(1, -1))
        vertex = knee.get_center()
        p1 = vertex + angleArcRadii * (leg.get_unit_vector())
        p2 = vertex + angleArcRadii * (-servoShaft.get_unit_vector())
        # The fourth point is offset from vertex by both vectors
        p3 = vertex + angleArcRadii * (leg.get_unit_vector() - servoShaft.get_unit_vector())
        legServoSquareAngleFill = Polygon(vertex, p1, p3, p2, fill_color=PURPLE, fill_opacity=0.7, stroke_width=0)

        zLineyLineSquareAngle = RightAngle(hipSeperationDashedLine, yDashedLine, length=angleArcRadii, color=WHITE, quadrant=(-1, -1))
        vertex = yDashedLine.get_top()
        p1 = vertex + angleArcRadii * (-hipSeperationDashedLine.get_unit_vector())
        p2 = vertex + angleArcRadii * (-yDashedLine.get_unit_vector())
        # The fourth point is offset from vertex by both vectors
        p3 = vertex + angleArcRadii * (-hipSeperationDashedLine.get_unit_vector() - yDashedLine.get_unit_vector())
        zLineyLineSquareAngleFill = Polygon(vertex, p1, p3, p2, fill_color=PURPLE, fill_opacity=0.7, stroke_width=0)

        triangle1 = Polygon(fLine.start, fLine.end, yDashedLine.end, stroke_color=ORANGE, fill_color=ORANGE, fill_opacity=0.7)
        triangle2 = Polygon(fLine.start, fLine.end, knee.get_center(), stroke_color=GREEN, fill_color=GREEN, fill_opacity=0.7)



        servoShaft.set_z_index(100)
        servoCentre.set_z_index(100)
        hipSeperationDashedLine.set_z_index(100)
        knee.set_z_index(100)
        leg.set_z_index(100)
        foot.set_z_index(100)
        fLine.set_z_index(100)
        fLineLabel.set_z_index(100)
        yDashedLine.set_z_index(100)
        legOrigin.set_z_index(100)
        





        hipAngleEquation = VGroup(
            MathTex(r"\theta_h ", color=GRAY),
            MathTex(r"=", color=WHITE),
            MathTex(r"\theta_h^{\prime}", color=ORANGE),
            MathTex(r"+", color=WHITE),
            MathTex(r"\theta_h^{\prime\prime}", color=GREEN)
        ).arrange(RIGHT).move_to(RIGHT*4 + UP)

        hipAngle1Equation = MathTex(r"\theta_h^{\prime} = \arctan\left(\frac{y}{q}\right)").move_to(hipAngleEquation.get_center() + DOWN*1.5)
        hipAngle1Equation[0][11].set_color(MAROON_A)
        hipAngle1Equation[0][13].set_color(YELLOW)
        hipAngle1Equation[0][0].set_color(ORANGE)
        hipAngle1Equation[0][1].set_color(ORANGE)
        hipAngle1Equation[0][2].set_color(ORANGE)


        hipAngle1EquationBox = SurroundingRectangle(hipAngle1Equation, color=ORANGE, buff=0.2)
        hipAngle1EquationBox.move_to(hipAngle1Equation.get_center())
        

        hipAngle2Equation = MathTex(r"\theta_h^{\prime\prime} = \arctan\left(\frac{b}{a}\right)").move_to(hipAngle1Equation.get_center() + DOWN*1.75)
        hipAngle2Equation[0][12].set_color(RED)
        hipAngle2Equation[0][14].set_color(LIGHT_PINK)
        hipAngle2Equation[0][0].set_color(GREEN)
        hipAngle2Equation[0][1].set_color(GREEN)
        hipAngle2Equation[0][2].set_color(GREEN)
        hipAngle2Equation[0][3].set_color(GREEN)

        hipAngle2EquationBox = SurroundingRectangle(hipAngle2Equation, color=GREEN, buff=0.2)
        hipAngle2EquationBox.move_to(hipAngle2Equation.get_center())

        hipEquations = VGroup(hipAngleEquation, hipAngle1EquationBox, hipAngle2EquationBox)
        hipEquationsBox = SurroundingRectangle(hipEquations, color=GRAY, buff=0.2)
        hipEquationsBox.move_to(hipEquations.get_center())

        triangle1PythagEquation = VGroup(
            MathTex(r"f^{2}", color=GOLD),
            MathTex(r"=", color=WHITE),
            MathTex(r"q^{2}", color=YELLOW),
            MathTex(r"+", color=WHITE),
            MathTex(r"y^{2}", color=MAROON_A),
        ).arrange(RIGHT).move_to(RIGHT*4 + UP*3)

        triangle1EquationBox = SurroundingRectangle(triangle1PythagEquation, color=ORANGE, buff=0.2)
        triangle1EquationBox.move_to(triangle1PythagEquation.get_center())

        triangle2PythagEquation = VGroup(
            MathTex(r"f^{2}", color=GOLD),
            MathTex(r"=", color=WHITE),
            MathTex(r"b^{2}", color=RED),
            MathTex(r"+", color=WHITE),
            MathTex(r"a^{2}", color=LIGHT_PINK),
        ).arrange(RIGHT).move_to(RIGHT*4 + UP*1.5)

        triangle2EquationBox = SurroundingRectangle(triangle2PythagEquation, color=GREEN, buff=0.2)
        triangle2EquationBox.move_to(triangle2PythagEquation.get_center())

        triangleEqualEquation = VGroup(
            MathTex(r"b^{2}", color=RED),
            MathTex(r"+", color=WHITE),
            MathTex(r"a^{2}", color=LIGHT_PINK),
            MathTex(r"=", color=WHITE),
            MathTex(r"q^{2}", color=YELLOW),
            MathTex(r"+", color=WHITE),
            MathTex(r"y^{2}", color=MAROON_A)
        ).arrange(RIGHT).move_to(RIGHT*4.5 + UP*3)

        bSquaredEqualEquation = VGroup(
            MathTex(r"b^{2}", color=RED),
            MathTex(r"=", color=WHITE),
            MathTex(r"q^{2}", color=YELLOW),
            MathTex(r"+", color=WHITE),
            MathTex(r"y^{2}", color=MAROON_A),
            MathTex(r"-", color=WHITE),
            MathTex(r"a^{2}", color=LIGHT_PINK),
        ).arrange(RIGHT).move_to(RIGHT*4.4 + UP*3)

        bSubjectEquation = MathTex(
            r"b = \sqrt{q^{2} + y^{2} - a^{2}}",
            substrings_to_isolate=["b", "=", r"\sqrt{", "q^{2}", "+", "y^{2}", "-", "a^{2}"]
        )
        # Set colors
        bSubjectEquation.set_color_by_tex("b", RED)
        bSubjectEquation.set_color_by_tex("q^{2}", YELLOW)
        bSubjectEquation.set_color_by_tex("y^{2}", MAROON_A)
        bSubjectEquation.set_color_by_tex("a^{2}", LIGHT_PINK)
        bEquationBox = SurroundingRectangle(bSubjectEquation, color=RED, buff=0.2)
        bSubjectEquation.move_to(ORIGIN + RIGHT*4 + UP*3)
        bEquationBox.move_to(bSubjectEquation.get_center())




        #DRAW LEG
        self.play(
             LaggedStart(
                  Create(servoCentre),
                  Create(servoShaft),
                  Create(knee), 
                  Create(leg),
                  Create(foot),
                  lag_ratio=0.3
             )
        )
        
        self.play(
            LaggedStart(
                 (Create(hipSeperationDashedLine), Create(legOrigin)),
                 Create(yDashedLine),
                 Create(zDashedLine),
                 (Create(yArrow), Create(yLabel)),
                 (Create(zArrow), Create(zLabel)),
                 Create(hipAngleArc),
                 lag_ratio=0.3
            )
        )


        
        


        self.play(FadeIn(hipAngleSector))

        self.play(Create(hipAngleLabel))
        self.play(Create(legArrow), Create(legArrowLabel))



        self.play(
            LaggedStart(
                 Create(legServoSquareAngle),
                 FadeIn(legServoSquareAngleFill),
                 Create(zLineyLineSquareAngle),
                 FadeIn(zLineyLineSquareAngleFill)
            )
        )

        self.play(
             FadeOut(hipAngleLabel),
             Create(fLine),
             Create(fLineLabel)
        )

        
        


        self.play(Create(qArrow), Create(qLineLabel), Create(servoShaftArrow), Create(servoShaftLabel))
        self.wait(2)

        #TRIANGLES

        trianglePulseTime = 0.5

        self.play(FadeIn(triangle1), run_time=trianglePulseTime)
        
        self.play(
             Write(triangle1PythagEquation),
             Create(triangle1EquationBox)
             )
        self.play(FadeOut(triangle1), run_time=trianglePulseTime)
        self.wait(1)
        self.play(FadeIn(triangle2), run_time=trianglePulseTime)
        
        self.play(
             Write(triangle2PythagEquation),
             Create(triangle2EquationBox)
             )
        self.play(FadeOut(triangle2), run_time=trianglePulseTime)


        
        
        self.wait(2)
        #REARRANGE FOR B

        self.play(
            FadeOut(triangle1EquationBox),
            FadeOut(triangle2EquationBox),
            FadeOut(triangle1PythagEquation[0]),
            FadeOut(triangle2PythagEquation[0]),
            FadeOut(triangle2PythagEquation[1]),
            *[mob.animate.move_to(mob.get_center() + RIGHT*1.1) for i, mob in enumerate(triangle1PythagEquation) if i != 0],
            *[mob.animate.move_to(mob.get_center() + LEFT*1.4 + UP*1.5) for i, mob in enumerate(triangle2PythagEquation) if i not in [0,1]]
        )
        self.wait(1)

        self.remove(*triangle1PythagEquation, *triangle2PythagEquation)
        self.add(triangleEqualEquation)

        self.play(TransformMatchingTex(triangleEqualEquation, bSquaredEqualEquation))

        self.wait(1)

        self.play(TransformMatchingTex(bSquaredEqualEquation, bSubjectEquation))
        self.wait(1)
        self.play(Create(bEquationBox))
        self.wait(2)

        #SPLIT HIP ANGLE
        self.play(
             FadeOut(hipAngleArc),
             FadeOut(hipAngleSector),
        )

        self.play(Create(hipAngle1Arc), Create(hipAngle2Arc))
        self.play(FadeIn(hipAngle1Sector), FadeIn(hipAngle2Sector))

        self.wait(2)
        #HIP ANGLE EQUATIONS
        self.play(
            LaggedStart(
                 Write(hipAngleEquation),
                 (Write(hipAngle1Equation), Create(hipAngle1EquationBox)),
                 (Write(hipAngle2Equation), Create(hipAngle2EquationBox)),
                 Create(hipEquationsBox),
                 lag_ratio=0.3
            )
        )

        self.wait(2)

        




        
        
        
        
        return

class FrontView(Scene):
     def construct(self):
          servoCentrePoint = Dot(manim.ORIGIN + UP *2.5, color=BLUE)
          leftServoCentre = Dot(color=GREEN).move_to(servoCentrePoint.get_center() + LEFT * (convertDistance(servoDistance)/2)).set_z_index(50)
          rightServoCentre = Dot(color=GREEN).move_to(servoCentrePoint.get_center() + RIGHT * (convertDistance(servoDistance)/2)).set_z_index(50)

          footXVal = ValueTracker(0)
          footYVal = ValueTracker(footY)

          dashLength = 0.2
          def getNumDashes(radius):
              cirumference = math.pi * 2 * radius
              return int(cirumference / (2 * dashLength))

          foot = always_redraw(lambda:
              Dot(color=RED).move_to(servoCentrePoint.get_center() + RIGHT * convertDistance(footXVal.get_value()) + DOWN * convertDistance(footYVal.get_value()))
          )

          staticFoot = Dot(color=RED).move_to(servoCentrePoint.get_center() + RIGHT * convertDistance(footX) + DOWN * convertDistance(footY)).set_z_index(50)

          intersectionPoints = getAllIntersectionPoints(footXVal.get_value(), footYVal.get_value(), servoCentrePoint.get_center())

          leftServoIntersectionPoint = intersectionPoints[1]
          rightServoIntersectionPoint = intersectionPoints[2]

          leftThigh = always_redraw(
              lambda: Line(leftServoCentre.get_center(), leftServoIntersectionPoint.get_center(), color=GREEN).set_z_index(50))
          rightThigh = always_redraw(
              lambda: Line(rightServoCentre.get_center(), rightServoIntersectionPoint.get_center(), color=GREEN).set_z_index(50))
          
          leftCalf = always_redraw(
              lambda: Line(foot.get_center(), leftServoIntersectionPoint.get_center(), color=RED))
          rightCalf = always_redraw(
              lambda: Line(foot.get_center(), rightServoIntersectionPoint.get_center(), color=RED))



          for i, dot in enumerate(intersectionPoints):
              dot.add_updater(lambda mob, i=i: mob.move_to(
                  getAllIntersectionPoints(footXVal.get_value(), footYVal.get_value(), servoCentrePoint.get_center())[i]
                  .get_center()
              ))
              #self.add(dot)

              if dot.get_x() < leftServoIntersectionPoint.get_x():
                  leftServoIntersectionPoint = dot
                  print("left intersection changed to")
                  print(dot.get_center())

              if dot.get_x() > rightServoIntersectionPoint.get_x():
                  rightServoIntersectionPoint = dot

          def getSweepStartingAngle(sweep):
              vector = sweep.get_end() - sweep.get_start()
              angle = np.arctan2(vector[1], vector[0])
              return angle
          
          leftThighStartingAngle = getSweepStartingAngle(leftThigh)
          rightThighStartingAngle = getSweepStartingAngle(rightThigh)
          footStartingAngle = getSweepStartingAngle(leftCalf)

          

          arc_progress = ValueTracker(0)
          total_angle = -2 * PI  # or whatever sweep you want

          def progressive_dashed_arc(arcRadius, arcCentre, startingAngle):
            progress = arc_progress.get_value()
            dash_length = dashLength
            gap_length = dashLength
            radius = convertDistance(arcRadius)
            start_angle = startingAngle
            sweep_angle = progress * total_angle
            sign = np.sign(sweep_angle) if sweep_angle != 0 else 1
            arc_len = abs(sweep_angle) * radius
            pattern_length = dash_length + gap_length
            n_dashes = int(arc_len // pattern_length) + 1
            dashes = VGroup()
            angle_drawn = 0
            for i in range(n_dashes):
                dash_start_angle = start_angle + angle_drawn / radius * sign
                # How much of this dash should be visible?
                remaining_arc = arc_len - angle_drawn
                this_dash_length = min(dash_length, max(0, remaining_arc))
                if this_dash_length <= 0:
                    break
                dash_angle = this_dash_length / radius * sign
                dashes.add(Arc(
                    start_angle=dash_start_angle,
                    angle=dash_angle,
                    radius=radius,
                    arc_center=arcCentre
                ))
                angle_drawn += pattern_length
            return dashes

          leftServoDashedArc = always_redraw(lambda: progressive_dashed_arc(thighLength, leftServoCentre.get_center(), leftThighStartingAngle))
          rightServoDashedArc = always_redraw(lambda: progressive_dashed_arc(thighLength, rightServoCentre.get_center(), rightThighStartingAngle))
          footDashedArc = always_redraw(lambda: progressive_dashed_arc(calfLength, staticFoot.get_center(), footStartingAngle))

          leftServoDashedLine = DashedLine(leftServoCentre.get_center(), servoCentrePoint.get_center(), dash_length=dashLength/2).set_z_index(10)
          rightServoDashedLine = DashedLine(rightServoCentre.get_center(), servoCentrePoint.get_center(), dash_length=dashLength/2).set_z_index(10)

          leftServoAngleArc = Angle(leftServoDashedLine, leftThigh, radius=0.5, other_angle=True).set_z_index(10)
          rightServoAngleArc = Angle(rightServoDashedLine, rightThigh, radius=0.5).set_z_index(10)

          leftServoAngleLabel = MathTex(r'\theta_l').move_to(leftServoAngleArc.get_center()).scale(0.6)
          rightServoAngleLabel = MathTex(r'\theta_r').move_to(rightServoAngleArc.get_center()).scale(0.6)

          footBLine = DashedLine(servoCentrePoint.get_center(), foot.get_center(), dash_length=dashLength/2)
          footBArrow = getDimensionArrowFromLine(footBLine, offset=0.25, tip_shape=StealthTip).set_z_index(50)
          footBLabel = MathTex('b').move_to(footBArrow.get_center() + RIGHT * 0.2)

          footXArrow = Arrow(foot.get_center() + LEFT*0.2, foot.get_center() + RIGHT, stroke_width=3, tip_shape=StealthTip)
          footXLabel = MathTex('x').move_to(footXArrow.get_end() + RIGHT * 0.4)

          self.play(Create(rightServoCentre),
                    Create(leftServoCentre),
                    Create(foot)
                    )
          
          self.play(Create(leftThigh),
                    Create(rightThigh),
                    Create(leftCalf),
                    Create(rightCalf)
                    )
                   
          staticLeftCalf = Line(leftCalf.get_start(), leftCalf.get_end(), color=RED)

          self.remove(leftCalf)
          self.add(staticLeftCalf)
          self.add(staticFoot)
          self.remove(foot)

          self.add(leftServoDashedArc, rightServoDashedArc, footDashedArc)
          
          self.wait(1)

          bLine = AnimationGroup(
              Create(footBLine),
              FadeIn(leftServoDashedLine),
              FadeIn(rightServoDashedLine)
          )

          bArrow = AnimationGroup(
            Create(footBArrow),
            Create(footBLabel))
          
          xLine = AnimationGroup(
              Create(footXLabel),
              Create(footXArrow)
          )

          self.play(AnimationGroup(
              bLine,
              bArrow,
              xLine,
              lag_ratio=0.5
          ))   

          self.wait(1)

          self.play(
              FadeOut(footBArrow),
              FadeOut(footBLine),
              FadeOut(footBLabel),
              FadeOut(leftServoDashedLine),
              FadeOut(rightServoDashedLine),
              FadeOut(footXArrow),
              FadeOut(footXLabel)
          )

          self.wait(1)

          self.play(
            Rotate(leftThigh, total_angle, about_point=leftThigh.get_start()),
            Rotate(rightThigh, total_angle, about_point=rightThigh.get_start()),
            Rotate(staticLeftCalf, total_angle, about_point=staticFoot.get_start()),
            arc_progress.animate.set_value(1),
            run_time=3
        )
          self.wait(1)
          
          
          self.play(FadeIn(intersectionPoints[0]),
                    FadeIn(intersectionPoints[1]),
                    FadeIn(intersectionPoints[2]),
                    FadeIn(intersectionPoints[3]),)
          
          self.remove(staticLeftCalf)
          self.add(leftCalf, foot)
          
          

          staticFoot.add_updater(lambda m: m.move_to(foot.get_center()))
          
          

          
          

          self.play(footYVal.animate.set_value(95), footXVal.animate.set_value(-30), run_time=1)
          self.play(footYVal.animate.set_value(115), footXVal.animate.set_value(40), run_time=1)
          self.play(footYVal.animate.set_value(footY), footXVal.animate.set_value(0), run_time=1)

          self.wait(1)

          self.play(FadeOut(footDashedArc), 
                    FadeOut(leftServoDashedArc),
                    FadeOut(rightServoDashedArc),
                    FadeOut(intersectionPoints[0]),
                    FadeOut(intersectionPoints[3]))
          

          self.wait(1)


          pulseDuration = 0.5
          pulseScale=1.8
          self.play(leftServoCentre.animate.scale(pulseScale), 
                    rightServoCentre.animate.scale(pulseScale),
                    run_time=pulseDuration)
          
          self.play(leftServoCentre.animate.scale(1/pulseScale), 
                    rightServoCentre.animate.scale(1/pulseScale),
                    run_time=pulseDuration)
          
          self.play(
                    intersectionPoints[1].animate.scale(pulseScale),
                    intersectionPoints[2].animate.scale(pulseScale),
                    run_time=pulseDuration)
          
          self.play(
                    intersectionPoints[1].animate.scale(1/pulseScale),
                    intersectionPoints[2].animate.scale(1/pulseScale),
                    run_time=pulseDuration)


          self.wait(1)

          lineDraw = AnimationGroup(
              Create(leftServoDashedLine),
              Create(rightServoDashedLine))

          arcDraw = AnimationGroup(
              Create(leftServoAngleArc),
              Create(rightServoAngleArc))
          
          labelDraw = AnimationGroup(
              Create(leftServoAngleLabel),
              Create(rightServoAngleLabel))
          
          self.play(
              AnimationGroup(
                  lineDraw,
                  arcDraw,
                  labelDraw,
                  lag_ratio=0.8
              )
          )

          self.wait(1)

          self.play(
              FadeOut(leftServoAngleArc),
              FadeOut(rightServoAngleArc),
              FadeOut(leftServoAngleLabel),
              FadeOut(rightServoAngleLabel),
              FadeOut(leftServoDashedLine),
              FadeOut(rightServoDashedLine)
          )

          self.wait(2)          

class IkEquation(Scene):
    def construct(self):
        equation = MathTex(
            r'f(x, y, z) = [\theta_l, \theta_r, \theta_h]',
            substrings_to_isolate=[
                'x, y, z',
                r'\theta_l, \theta_r, \theta_h'
                ]
            ).scale(2)
        
        self.play(Write(equation))
        
        self.play(equation.animate.set_color_by_tex('x, y, z', RED))
        self.play(equation.animate.set_color_by_tex('x, y, z', WHITE))
        self.wait(0.5)
        self.play(equation.animate.set_color_by_tex(r'\theta_l, \theta_r, \theta_h', TEAL))
        self.play(equation.animate.set_color_by_tex(r'\theta_l, \theta_r, \theta_h', WHITE))

        self.play(Unwrite(equation))

        self.wait(1)


class TickBox(Scene):
    def construct(self):
        image = SVGMobject("tickbox.svg")
        image.set(height=3)
        image.set_stroke(color=WHITE, width=3)

        self.play(Create(image), run_time=3)
        self.wait(0.5)

