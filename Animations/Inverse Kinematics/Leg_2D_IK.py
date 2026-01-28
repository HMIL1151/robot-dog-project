import manim
from manim import *
import math

config.background_color = "#020B15"

thighLength = 30
calfLength = 120
servoDistance = 46
hipSeperation = 160
servoAxisDistance = 31.56
footZ = 10
footY = 125

arcRadii = 10


divisor = 22

def convertDistance(value):
    return value / divisor

def createRelativePoint(robotOrigin:Dot, x, y):
        xDisplay = convertDistance(x)
        yDisplay = convertDistance(y)

        origin = robotOrigin.get_center()

        originX = origin[0]
        originY = origin[1]

        return Dot(point=[originX - xDisplay, originY - yDisplay, 0])

def dimension_arrow_from_line(
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

        legArrow = dimension_arrow_from_line(leg, color=RED, offset=-0.4)
        legArrowLabel = MathTex('b', color=RED).move_to(legArrow.get_midpoint() + LEFT*0.2 + DOWN*0.2)
        servoShaftArrow = dimension_arrow_from_line(servoShaft, offset=-0.2, stroke_color=LIGHT_PINK)
        servoShaftLabel = MathTex('a', color=LIGHT_PINK).move_to(servoShaftArrow.get_midpoint() + UP*0.4)
        yDashedLine = DashedLine(foot.get_center(), [foot.get_center()[0], legOrigin.get_center()[1], 0])
        zDashedLine = DashedLine(foot.get_center(), [legOrigin.get_center()[0], foot.get_center()[1], 0])

        hipSeperationDashedLine = DashedLine(servoCentre.get_center(), legOrigin.get_center())
        hipSeperationArrow = dimension_arrow_from_line(hipSeperationDashedLine, offset=0.2)
        hipSeperationLabel = MathTex('d/2').move_to(hipSeperationArrow.get_midpoint() + UP*0.3 + RIGHT*0.2)

        qLine = Line(servoCentre.get_center(), [foot.get_center()[0], legOrigin.get_center()[1], 0])
        qArrow = dimension_arrow_from_line(qLine, offset=0.2, stroke_color=YELLOW)
        qLineLabel = MathTex('q', color=YELLOW).next_to(qArrow, UP*0.4)
        
        yArrow = dimension_arrow_from_line(yDashedLine, offset=-0.4, stroke_color=MAROON_A)
        yLabel = MathTex('y', color=MAROON_A).next_to(yArrow, RIGHT*0.4)
        zArrow = dimension_arrow_from_line(zDashedLine, offset=0.2, stroke_color=TEAL).shift(UP * convertDistance(footY))
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

