from manim import *
import numpy as np

class TriangleCircumcircle(Scene):
    def construct(self):
        # 样式配置
        TEXT_COLOR = WHITE
        LINE_COLOR = BLUE
        ARC_COLOR = GREEN
        PERP_COLOR = ORANGE
        CIRCLE_COLOR = RED
        config.background_color = BLACK

        # 1. 标题（用Text而非MathTex，避免LaTeX）
        title = Text("三角形外接圆尺规作图", font_size=30, color=TEXT_COLOR).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # 2. 画三角形ABC
        A = np.array([-2, 1, 0])
        B = np.array([1, 2, 0])
        C = np.array([-0.5, -1, 0])
        triangle = Polygon(A, B, C, color=LINE_COLOR, fill_opacity=0, stroke_width=2)
        dots = [Dot(p, color=TEXT_COLOR, radius=0.08) for p in [A, B, C]]
        labels = [Text(name, font_size=20, color=TEXT_COLOR).next_to(p, dir) 
                  for name, p, dir in zip(["A", "B", "C"], [A, B, C], [LEFT, RIGHT, DOWN])]
        
        self.play(Create(triangle), *[Create(d) for d in dots], *[Write(l) for l in labels])
        self.wait(1)

        # 3. 作AB的垂直平分线（核心修正：扩大圆弧范围+半径，确保相交）
        seg_AB = Line(A, B)
        ab_radius = seg_AB.get_length()
        # 3.1 以A为圆心画弧（覆盖AB两侧，角度范围扩大到±120°）
        arc1 = self.get_intersecting_arc(A, B, ab_radius, ARC_COLOR)
        self.play(Create(arc1), run_time=1)
        # 用Text标注（避免LaTeX）
        label_arc1 = Text("以A为圆心，AB为半径画弧", font_size=18, color=ARC_COLOR).to_edge(RIGHT).shift(UP*2)
        self.play(Write(label_arc1))
        
        # 3.2 以B为圆心画弧（同半径、同角度范围）
        arc2 = self.get_intersecting_arc(B, A, ab_radius, ARC_COLOR)
        self.play(Create(arc2), run_time=1)
        # 更新标注
        self.play(Transform(label_arc1, Text("以B为圆心，AB为半径画弧", font_size=18, color=ARC_COLOR).to_edge(RIGHT).shift(UP*2)))
        
        # 3.3 找圆弧交点，画垂直平分线
        arc1_points = self.get_arc_sample_points(arc1)
        arc2_points = self.get_arc_sample_points(arc2)
        intersects = self.find_arc_intersections(arc1_points, arc2_points)
        # 用两个交点画垂直平分线
        mid_AB = (A+B)/2
        if len(intersects) >= 2:
            perp_AB = DashedLine(intersects[0], intersects[1], 
                                 color=PERP_COLOR, stroke_width=2, dash_length=0.2)
        else:  # 备用方案：法向量生成（防止极端情况）
            perp_dir = np.array([B[1]-A[1], A[0]-B[0], 0])
            perp_dir = perp_dir / np.linalg.norm(perp_dir) * 3
            perp_AB = DashedLine(mid_AB - perp_dir, mid_AB + perp_dir, 
                                 color=PERP_COLOR, stroke_width=2, dash_length=0.2)
        
        # 画垂直平分线并添加标注
        self.play(Create(perp_AB), run_time=1)
        self.play(Transform(label_arc1, Text("连接弧的交点，作AB的垂直平分线", font_size=18, color=PERP_COLOR).to_edge(RIGHT).shift(UP*2)))
        
        # 添加直角符号：AB与垂直平分线的垂足
        right_angle_AB = RightAngle(seg_AB, perp_AB, length=0.3, color=PERP_COLOR, stroke_width=1.5)
        self.play(Create(right_angle_AB))
        self.wait(0.5)
        
        self.play(FadeOut(arc1), FadeOut(arc2), FadeOut(label_arc1), run_time=0.5)

        # 4. 作BC的垂直平分线（同逻辑修正）
        seg_BC = Line(B, C)
        bc_radius = seg_BC.get_length()
        arc3 = self.get_intersecting_arc(B, C, bc_radius, ARC_COLOR)
        self.play(Create(arc3), run_time=1)
        # 添加标注
        label_arc3 = Text("以B为圆心，BC为半径画弧", font_size=18, color=ARC_COLOR).to_edge(RIGHT).shift(UP*1)
        self.play(Write(label_arc3))
        
        arc4 = self.get_intersecting_arc(C, B, bc_radius, ARC_COLOR)
        self.play(Create(arc4), run_time=1)
        # 更新标注
        self.play(Transform(label_arc3, Text("以C为圆心，BC为半径画弧", font_size=18, color=ARC_COLOR).to_edge(RIGHT).shift(UP*1)))
        
        # 找BC圆弧交点，画垂直平分线
        arc3_points = self.get_arc_sample_points(arc3)
        arc4_points = self.get_arc_sample_points(arc4)
        bc_intersects = self.find_arc_intersections(arc3_points, arc4_points)
        mid_BC = (B+C)/2
        if len(bc_intersects) >= 2:
            perp_BC = DashedLine(bc_intersects[0], bc_intersects[1], 
                                 color=PERP_COLOR, stroke_width=2, dash_length=0.2)
        else:
            perp_dir_BC = np.array([C[1]-B[1], B[0]-C[0], 0])
            perp_dir_BC = perp_dir_BC / np.linalg.norm(perp_dir_BC) * 3
            perp_BC = DashedLine(mid_BC - perp_dir_BC, mid_BC + perp_dir_BC, 
                                 color=PERP_COLOR, stroke_width=2, dash_length=0.2)
        
        # 画BC的垂直平分线并添加标注
        self.play(Create(perp_BC), run_time=1)
        self.play(Transform(label_arc3, Text("连接弧的交点，作BC的垂直平分线", font_size=18, color=PERP_COLOR).to_edge(RIGHT).shift(UP*1)))
        
        # 添加直角符号：BC与垂直平分线的垂足
        right_angle_BC = RightAngle(seg_BC, perp_BC, length=0.3, color=PERP_COLOR, stroke_width=1.5)
        self.play(Create(right_angle_BC))
        self.wait(0.5)
        
        self.play(FadeOut(arc3), FadeOut(arc4), FadeOut(label_arc3), run_time=0.5)

        # 5. 找外心O
        O = line_intersection(perp_AB.get_start(), perp_AB.get_end(), 
                              perp_BC.get_start(), perp_BC.get_end())
        dot_O = Dot(O, color=CIRCLE_COLOR, radius=0.1)
        # 混合Text+MathTex（仅数学符号用LaTeX）
        label_O = VGroup(
            Text("O", font_size=20, color=CIRCLE_COLOR)
        ).arrange(RIGHT).next_to(O, UP)
        self.play(Create(dot_O), Write(label_O), run_time=1)
        # 添加外心定义标注
        label_centroid = Text("O为外心，外心为三角形三边垂直平分线的交点", font_size=18, color=CIRCLE_COLOR).to_edge(RIGHT)
        self.play(Write(label_centroid))
        self.wait(1)

        # 6. 画外接圆
        circum_circle = Circle(arc_center=O, radius=np.linalg.norm(A-O), 
                               color=CIRCLE_COLOR, stroke_width=2)
        self.play(Create(circum_circle), run_time=2)
        # 更新标注
        self.play(Transform(label_centroid, Text("外接圆：以O为圆心，OA为半径画圆", font_size=18, color=CIRCLE_COLOR).to_edge(RIGHT)))
        self.wait(1)
        
        # 隐藏辅助元素
        self.play(FadeOut(label_O),
                  FadeOut(dot_O),
                  FadeOut(perp_BC),
                  FadeOut(perp_AB),
                  FadeOut(right_angle_AB),
                  FadeOut(right_angle_BC),
                  FadeOut(label_centroid))
        self.wait(3)

    def get_intersecting_arc(self, center, target, radius, color):
        """生成能与对侧圆弧相交的大角度圆弧"""
        vec = target - center
        base_angle = angle_of_vector(vec)
        # 圆弧范围：从base_angle - 120° 到 base_angle + 120°（覆盖范围足够大）
        start_angle = base_angle - 2*PI/3
        end_angle = base_angle + 2*PI/3
        arc = Arc(
            arc_center=center,
            radius=radius,
            start_angle=start_angle,
            angle=end_angle - start_angle,  # 总角度240°，确保覆盖线段两侧
            color=color,
            stroke_width=1.2
        )
        return arc

    def get_arc_sample_points(self, arc, sample_count=100):
        """采样圆弧上的点，用于找交点"""
        points = []
        center = arc.get_arc_center()
        radius = arc.get_radius()
        start_angle = arc.get_start_angle()
        angle_range = arc.get_angle()
        # 均匀采样圆弧上的点
        for i in range(sample_count):
            t = i / (sample_count - 1)
            angle = start_angle + t * angle_range
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            points.append(np.array([x, y, 0]))
        return np.array(points)

    def find_arc_intersections(self, points1, points2, threshold=0.1):
        """找两段圆弧的交点（距离小于阈值即判定为交点）"""
        intersections = []
        for p1 in points1:
            for p2 in points2:
                if np.linalg.norm(p1 - p2) < threshold:
                    # 去重：避免重复添加相近的点
                    if not any(np.linalg.norm(p1 - p) < threshold for p in intersections):
                        intersections.append((p1 + p2) / 2)  # 取中点提高精度
        return intersections

# 辅助函数：求两直线交点（增加鲁棒性）
def line_intersection(p1, p2, p3, p4):
    x1,y1 = p1[:2]; x2,y2 = p2[:2]; x3,y3 = p3[:2]; x4,y4 = p4[:2]
    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(denom) < 1e-8:
        return np.array([0, 0, 0])
    t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4))/denom
    return np.array([x1 + t*(x2-x1), y1 + t*(y2-y1), 0])
