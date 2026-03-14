from manim import *

class TickBox(Scene):
    def construct(self):

        def getTickBoxes(completedTasks: list, incompleteTasks: list):
            height = 5.5
            topLocation = ORIGIN + UP*(height/2) + LEFT*3

            tickBoxes = []
            taskCount = len(completedTasks) + len(incompleteTasks)

            for i in range(len(completedTasks)):
                image = SVGMobject("tickbox.svg")
                image.set(height=0.5)
            
                boxLocation = topLocation - UP *((i) * height/taskCount)
                box = image.submobjects[0].move_to(boxLocation)
                tick = image.submobjects[1].move_to(boxLocation)
                task = Text(completedTasks[i], font_size=20).move_to(boxLocation + RIGHT*0.5, LEFT)

                animation = AnimationGroup(
                    Create(box),
                    Create(tick),
                    Write(task)
                )

                tickBoxes.append(animation)

            for i in range(len(incompleteTasks)):
                box = SVGMobject("untickedbox.svg").submobjects[0]
                box.set(height=0.5)

                boxLocation = topLocation - UP *((i + len(completedTasks)) * height/taskCount)
                box.move_to(boxLocation)
                task = Text(incompleteTasks[i], font_size=20).move_to(boxLocation + RIGHT*0.5, LEFT)

                animation = AnimationGroup(
                    Create(box),
                    Write(task)
                )

                tickBoxes.append(animation)

            return tickBoxes
        
        completedTasks = [
            "Select Motors",
            "Design Leg",
            "Test Leg",
            "Solve Inverse Kinematics"
        ]

        incompleteTasks = [
            "Foot Path Tracking",
            "Step Trajectory",
            "Gait Patterns",
            "Orientation Control",
            "Control System",
            "FINALLY.... Design Robot"
        ]
        
        tickBoxes = getTickBoxes(completedTasks, incompleteTasks)

        for i in range(len(tickBoxes)):
            self.play(tickBoxes[i], run_time=1)
 




        
        self.wait(0.5)
