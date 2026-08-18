from manim import *
import numpy as np

# 手动实现向量夹角计算（弥补Manim 0.19.0中无内置angle_between_vectors的问题）
def angle_between_vectors(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
    # 防止浮点误差导致arccos参数超出[-1,1]
    cos_theta = np.clip(dot_product / norm_product, -1.0, 1.0)
    return np.arccos(cos_theta)

class CopyAngle(Scene):
    def construct(self):
        # -------------------------- 步骤1：创建已知角和新线段（替代射线） --------------------------
        A = ORIGIN  # 已知角顶点A
        B = A + 3 * LEFT + 1 * UP  # 已知角的一边AB上的点
        C = A + 3 * RIGHT + 2 * UP  # 已知角的另一边AC上的点
        O = A + 3 * DOWN  # 新角顶点O
        P = O + 4 * RIGHT  # 延长OP线段

        # 绘制已知角的两边和新角的初始边
        seg_ab = Line(A, B, color=BLUE)
        seg_ac = Line(A, C, color=BLUE)
        line_op = Line(O, P, color=GREEN)

        # 标注点
        labels = VGroup(
            Text("A", color=WHITE).next_to(A, UP, 0.2),
            Text("B", color=WHITE).next_to(B, LEFT, 0.2),
            Text("C", color=WHITE).next_to(C, RIGHT, 0.2),
            Text("O", color=WHITE).next_to(O, DOWN, 0.2),
            Text("P", color=WHITE).next_to(P, RIGHT, 0.2)
        )

        self.play(Create(seg_ab), Create(seg_ac), Create(line_op), Write(labels))
        self.wait(1)

        # -------------------------- 步骤2：已知角上画弧 --------------------------
        radius = 2
        angle_ab = angle_of_vector(B - A)  # 起始角度
        angle_ac = angle_of_vector(C - A)
        arc1_angle = angle_ac - angle_ab  # 弧的张角
        arc1 = Arc(
            arc_center=A,
            radius=radius,
            start_angle=angle_ab,
            angle=arc1_angle,
            color=YELLOW
        )
        # 求弧与AB、AC的交点D、E
        D = A + radius * (B - A) / np.linalg.norm(B - A)
        E = A + radius * (C - A) / np.linalg.norm(C - A)
        # 标注D、E
        labels_de = VGroup(
            Text("D", color=WHITE).next_to(D, LEFT + UP, 0.2),
            Text("E", color=WHITE).next_to(E, RIGHT + UP, 0.2)
        )

        self.play(Create(arc1), Write(labels_de))
        self.wait(1)

        # -------------------------- 步骤3：新角顶点画同半径弧 --------------------------
        angle_op = angle_of_vector(P - O)  # 起始角度
        arc2_angle = PI * 1.2  # 微调弧的张角（略大于180度）
        arc2 = Arc(
            arc_center=O,
            radius=radius,
            start_angle=angle_op-PI/10,
            angle=arc2_angle-PI/3,
            color=YELLOW
        )
        # 求弧与OP的交点F
        F = O + radius * (P - O) / np.linalg.norm(P - O)
        label_f = Text("F", color=WHITE).next_to(F, RIGHT, 0.2)

        self.play(Create(arc2), Write(label_f))
        self.wait(1)

        # -------------------------- 步骤4：量取DE长度，画弧找交点G（核心修改部分） --------------------------
        # 计算DE的长度（尺规作图的半径，不再缩小）
        de_length = np.linalg.norm(E - D)
        # 先计算出正确的G点（和原来一致，是数学上的交点）
        angle = angle_between_vectors(B - A, C - A)
        G = O + radius * rotate_vector((P - O)/np.linalg.norm(P - O), angle)
        # 【关键修改1】计算arc3的起始角度：从F指向O的向量角度（圆心F，起始点O方向）
        # 正确的向量是：O - F（从F到O的向量），用angle_of_vector计算角度
        arc3_start_angle = angle_of_vector(O - F)
        # 【关键修改2】计算arc3的张角：从F到O的向量 到 F到G的向量 的角度差
        arc3_end_angle = angle_of_vector(G - F)  # 从F到G的向量角度
        arc3_angle = arc3_end_angle - arc3_start_angle  # 张角=终点角度-起始角度
        # 【关键修改3】绘制arc3：半径用原始DE长度，角度绑定到G点
        arc3 = Arc(
            arc_center=F,
            radius=de_length,  # 恢复原始DE长度，不再缩小
            start_angle=arc3_start_angle-PI/10,  # 起始角度对准O方向
            angle=arc3_angle,  # 张角对准G点
            color=ORANGE
        )
        # 标注G点
        label_g = Text("G", color=WHITE).next_to(G, UP, 0.2)

        self.play(Create(arc3), Write(label_g))
        self.wait(1)

        # -------------------------- 步骤5：连接OG并延长 --------------------------
        G_extended = O + 1.5 * (G - O)  # 延长后的端点
        line_og = Line(O, G_extended, color=GREEN)  # 线段从O到延长后的点，穿过G

        self.play(Create(line_og))
        self.wait(1)

        # -------------------------- 步骤6：高亮显示两个角 --------------------------
        angle_original = Angle(seg_ac, seg_ab, radius=0.8, color=RED)
        angle_new = Angle(line_op, line_og, radius=0.8, color=RED)

        self.play(Create(angle_original), Create(angle_new))
        self.wait(1)
        self.play(FadeOut(angle_original), FadeOut(angle_new))
