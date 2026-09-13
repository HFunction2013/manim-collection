from manim import *
from math import sqrt
import os
import numpy as np

# ===================== 全局常量配置 =====================
k = 3  # 基础缩放因子
TEX_FONT_SIZE = 30
LABEL_FONT_SIZE = 20
DEFAULT_RUN_TIME = 0.5
ANGLE_RADIUS = 0.5

# ===================== LaTeX 中文模板 =====================
class CtexTemplate(TexTemplate):
    def __init__(self):
        super().__init__()
        self.tex_compiler = "xelatex"
        self.output_format = ".xdv"
        self.tex_compiler_args = [
            "-synctex=1", "-interaction=nonstopmode",
            "-halt-on-error", "-encoding=utf8"
        ]
        self.preamble = r"""
\usepackage{xeCJK}
\usepackage{fontspec}
\usepackage{amsmath}
\usepackage{amssymb}
\newcommand{\equalparallel}{{\,}^{\,/\!/}_{=\!\!=} {\,}}
\setCJKmainfont{Microsoft YaHei}
\setCJKsansfont{SimHei}
\setmainfont{Times New Roman}
"""

# ===================== 通用工具函数 =====================
def create_tex(txt):
    """创建带中文支持的Tex文本"""
    return Tex(
        txt,
        font_size=TEX_FONT_SIZE,
        tex_template=CtexTemplate()
    ).move_to([k, k/2, 0])

def create_dot(x, y, color=WHITE):
    """创建点对象"""
    return Dot([x, y, 0], radius=0.05, color=color)

def create_line(start, end, color=BLUE, stroke_width=2):
    """创建线段对象"""
    line_obj = Line(
        start.get_center(),
        end.get_center()
    )
    line_obj.set_color(color)
    line_obj.set_stroke(
        color=color,
        width=stroke_width
    )
    return line_obj

# 快捷创建青色点和线
create_fdot = lambda x, y: create_dot(x, y, TEAL)
create_fline = lambda start, end: create_line(start, end, TEAL)

# 简化版标签创建（直接传文本，跳过自动提取）
def create_label(obj, pos, text, color=WHITE, use_tex=False):
    if use_tex:
        return Tex(text,
                   font_size=LABEL_FONT_SIZE,
                   color=color
                ).next_to(obj, pos, buff=0.1)
    else:
        return Text(text,
                    font_size=LABEL_FONT_SIZE,
                    color=color
                ).next_to(obj, pos, buff=0.1)
create_flabel = lambda obj, pos, text, use_tex=True: create_label(obj, pos, text, TEAL, use_tex)

def highlight_line(line_obj, run_time=DEFAULT_RUN_TIME):
    """高亮线段"""
    if not hasattr(line_obj, 'original_style'):
        line_obj.original_style = {
            "stroke_color": line_obj.get_stroke_color(),
            "stroke_width": line_obj.get_stroke_width()
        }
    return AnimationGroup(
        line_obj.animate.set_color(RED).set_stroke(color=RED, width=8),
        run_time=run_time,
        lag_ratio=0
    )

def dehighlight_line(line_obj, run_time=DEFAULT_RUN_TIME):
    """取消线段高亮"""
    if hasattr(line_obj, 'original_style'):
        return AnimationGroup(
            line_obj.animate.set_color(line_obj.original_style["stroke_color"]),
            line_obj.animate.set_stroke(
                color=line_obj.original_style["stroke_color"],
                width=line_obj.original_style["stroke_width"]
            ),
            run_time=run_time,
            lag_ratio=0
        )
    return Wait(0)

def handle_angle(vertex, line1, line2, color=RED, opacity=0.5, 
                arc_radius=ANGLE_RADIUS, use_small_angle=True, 
                run_time=DEFAULT_RUN_TIME, return_anim=True):
    """统一处理角度标注"""
    v_center = vertex.get_center()
    vec1 = (line1.get_start() if not np.allclose(line1.get_start(), v_center) 
            else line1.get_end()) - v_center
    vec2 = (line2.get_start() if not np.allclose(line2.get_start(), v_center) 
            else line2.get_end()) - v_center
    
    angle1 = np.arctan2(vec1[1], vec1[0])
    angle2 = np.arctan2(vec2[1], vec2[0])
    
    if use_small_angle:
        delta = abs(angle2 - angle1)
        delta = delta if delta <= np.pi else 2 * np.pi - delta
        start_angle = min(angle1, angle2)
    else:
        delta = abs(angle2 - angle1)
        delta = delta if delta >= np.pi else 2 * np.pi - delta
        start_angle = max(angle1, angle2)
    
    sector = Sector(
        start_angle=start_angle,
        angle=delta,
        radius=arc_radius,
        fill_color=color,
        fill_opacity=opacity,
        stroke_width=0,
        stroke_color=color
    ).shift(v_center)
    
    if not hasattr(vertex, 'angle_sectors'):
        vertex.angle_sectors = {}
    sector_key = (id(line1), id(line2))
    vertex.angle_sectors[sector_key] = {"sector": sector, "run_time": run_time}
    
    if return_anim:
        return Create(sector, run_time=run_time)
    return sector

def dehighlight_angle(vertex, line1, line2, run_time=DEFAULT_RUN_TIME):
    """取消角度标注"""
    sector_key = (id(line1), id(line2))
    if hasattr(vertex, 'angle_sectors') and sector_key in vertex.angle_sectors:
        sector = vertex.angle_sectors[sector_key]["sector"]
        anim = FadeOut(sector, run_time=run_time)
        del vertex.angle_sectors[sector_key]
        return anim
    return Wait(run_time)

# ===================== 主场景类 =====================
class GeometryScene(Scene):
    def construct(self):
        def init_obj():
            # 1. 初始化几何对象
            self.A = create_dot(0, k)
            self.B = create_dot(-k, 0)
            self.C = create_dot(0, 0)
            self.D = create_dot(-k, k)
            self.P = create_dot(-k/2, (2 - sqrt(3))/2 * k)
            self.Q = create_fdot(k/2, (2 - sqrt(3))/2 * k)
            
            # 线段
            self.AB = create_line(self.A, self.B)
            self.BC = create_line(self.B, self.C)
            self.CA = create_line(self.C, self.A)
            self.AP = create_line(self.A, self.P)
            self.PB = create_line(self.P, self.B)
            self.PC = create_line(self.P, self.C)
            self.PQ = create_fline(self.P, self.Q)
            self.AQ = create_fline(self.A, self.Q)
            self.CQ = create_fline(self.C, self.Q)
            self.DP = create_fline(self.D, self.P)
            self.DB = create_fline(self.D, self.B)
            self.DA = create_fline(self.D, self.A)
            
            # 角度扇形（先创建，再创建标签）
            self.sec1 = handle_angle(self.C, self.BC, self.PC, return_anim=False)
            self.sec2 = handle_angle(self.C, self.CA, self.PC, YELLOW, return_anim=False)
            
            self.PCB = handle_angle(
                    self.C, self.PC, self.BC, color=RED, opacity=0.5, 
                    arc_radius=ANGLE_RADIUS, use_small_angle=True, 
                    run_time=DEFAULT_RUN_TIME, return_anim=False
                )
            
            self.APC = handle_angle(self.P, self.AP, self.PC, YELLOW, return_anim=False)
            self.QPC = handle_angle(self.P, self.PQ, self.PC, return_anim=False)
            
            # 标签
            self.lA = create_label(self.A, UP + RIGHT, "A")
            self.lB = create_label(self.B, LEFT + UP, "B")
            self.lC = create_label(self.C, RIGHT + UP, "C")
            self.lD = create_flabel(self.D, LEFT + UP, "D")
            self.lP = create_label(self.P, UP, "P")
            self.lQ = create_flabel(self.Q, RIGHT, "Q")
            self.lPCB = create_label(self.PCB, LEFT, r"$15^\circ$", use_tex=True)
            self.lQPC = create_label(self.QPC, RIGHT, "1")
            self.lAPC = create_label(self.APC, RIGHT, r"2", use_tex=True)
            self.lsec2 = create_label(self.sec2, UP, "2")
            self.lsec1 = create_label(self.sec1, LEFT, "1")
            
            # 信息文本
            self.info_text = create_tex("")
            
            self.ax = Axes([-6, 6, 1], [-6, 6, 1], 7, 7, tips=False)
            
            
            self.trAPC = Polygon(
                self.A.get_center(),
                self.P.get_center(),
                self.C.get_center(),
                color=BLUE,
                fill_opacity=0.3,
                stroke_width=2
            )
            
            self.trAPQ = Polygon(
                self.A.get_center(),
                self.P.get_center(),
                self.Q.get_center(),
                color=BLUE,
                fill_opacity=0.3,
                stroke_width=2
            )
        init_obj()
        self.add(self.info_text)

        # 2. 通用辅助方法
        def init_geometry():
            """初始化绘制"""
            self.play(
                Create(self.A), Write(self.lA),
                Create(self.B), Write(self.lB),
                Create(self.C), Write(self.lC),
                Create(self.AB), Create(self.BC), Create(self.CA),
                Create(self.P), Write(self.lP), Create(self.AP),
                Create(self.PB), Create(self.PC),
                run_time=1
            )
            self.add(self.info_text)
        
        def update_info(txt):
            """更新文本"""
            return Transform(
                       self.info_text,
                       create_tex(txt)
                   )
        
        def reset_scene(title):
            """重置场景"""
            self.wait(1)
            self.play(update_info(""))
            self.clear()
            self.play(
                Write(
                    Text(
                        title,
                        font_size=TEX_FONT_SIZE
                    )
                )
            )
            self.wait(1)
            self.clear()
            init_geometry()
            
        def present_problem():
             # 初始绘制ABC
            self.play(
                Create(self.A),
                Write(self.lA),
                Create(self.B),
                Write(self.lB),
                Create(self.C),
                Write(self.lC),
                Create(self.AB),
                Create(self.BC),
                Create(self.CA),
                update_info(r"在等腰直角$\triangle ABC$中")
            )
            self.wait(1.5) # 增加等待，让观众看清初始图形
            
            # 标注AC=BC
            self.play(
                highlight_line(self.CA),
                highlight_line(self.BC),
                update_info(r"$AC\,=\,BC$")
            )
            self.wait(1)
            self.play(
                dehighlight_line(self.CA),
                dehighlight_line(self.BC)
                )
            self.wait(0.5)
            
            # 标注∠ACB=90°
            self.play(
                handle_angle(self.C, self.CA, self.BC, ORANGE),
                update_info(r"$\angle ACB\,=\,90^\circ$")
            )
            self.wait(1)
            self.play(dehighlight_angle(self.C, self.CA, self.BC))
            self.wait(0.5)
            
            # 绘制P点
            self.play(
                Create(self.P),
                Write(self.lP),
                update_info(r"$P$ 为 $\triangle ABC$ 内部一点")
            )
            self.wait(0.5)
            self.play(
                Create(self.PB),
                Create(self.PC)
            )
            self.play(
                highlight_line(self.PB),
                highlight_line(self.PC),
                update_info(r"$PB\,=\,PC$")
            )
            self.wait(1)
            self.play(
                dehighlight_line(self.PB),
                dehighlight_line(self.PC)
            )
            self.wait(0.5)
            
            # 绘制AP并标注AP=AC
            self.play(Create(self.AP))
            self.play(
                highlight_line(self.AP),
                highlight_line(self.CA),
                update_info(r"$AP\,=\,AC$")
            )
            self.wait(1)
            self.play(
                dehighlight_line(self.AP),
                dehighlight_line(self.CA)
            )
            self.wait(0.5)
            
            # 提出问题
            self.play(update_info(r"求 $\angle BCP$"))
            self.wait(2) # 增加等待，强调问题
        
        def solution1():
            # 方法一：辅助线PQ推导
            reset_scene("方法一")
            
            # 标注∠1 ∠2
            self.play(
                Create(self.sec1),
                Create(self.lsec1),
                Wait(1),
                
                Create(self.sec2),
                Create(self.lsec2),
                Wait(1),
                
                Create(self.PQ),
                Create(self.Q),
                Write(self.lQ),
                update_info(r"作 $PQ \equalparallel BC$"),
                Wait(1.5),
                
                Create(self.AQ),
                Create(self.CQ),
                update_info(r"连接 $AQ, CQ$"),
                Wait(1.5),
                
                highlight_line(self.PQ),
                highlight_line(self.BC),
                update_info(r"$\because PQ // BC$"),
                Wait(1),
                
                dehighlight_line(self.PQ),
                dehighlight_line(self.BC),
                Wait(0.5),
                
                Create(self.QPC),
                Create(self.lQPC),
                update_info(r"$\therefore \angle QPC = \angle 1$"),
                Wait(1.5),
                
                highlight_line(self.AP),
                highlight_line(self.CA),
                update_info(r"$\because AP = AC$"),
                Wait(1),
                
                dehighlight_line(self.AP),
                dehighlight_line(self.CA),
                Wait(0.5),
                
                Create(self.trAPC),
                update_info(r"$\therefore \triangle APC$ 为等腰三角形"),
                Wait(1.5),
                
                FadeOut(self.trAPC),
                update_info(r"$\therefore \angle ACP = \angle APC$"),
                Wait(1.5),
                
                Create(self.APC),
                Create(self.lAPC),
                update_info(r"$\angle APC = \angle 2$"),
                Wait(1.5),
                
                update_info(r"$\therefore \angle APQ = \angle 2 - \angle 1$"),
                Wait(1.5),
                
                handle_angle(self.C, self.CA, self.BC, ORANGE),
                update_info(r"$\because \angle ACB\,=\,90^\circ$"),
                Wait(1),
                
                dehighlight_angle(self.C, self.CA, self.BC),
                update_info(r"$\therefore \angle 1 + \angle 2\,=\,90^\circ$"),
                Wait(1.5),
                
                highlight_line(self.PQ),
                highlight_line(self.BC),
                update_info(r"$\because PQ \equalparallel BC$"),
                Wait(1),
                
                dehighlight_line(self.PQ),
                dehighlight_line(self.BC),
                highlight_line(self.CQ),
                highlight_line(self.PB),
                highlight_line(self.PC),
                update_info(r"$\therefore CQ\,=\,PB\,=\,PC$"),
                Wait(1),
                
                dehighlight_line(self.CQ),
                dehighlight_line(self.PB),
                dehighlight_line(self.PC),
                highlight_line(self.AP),
                highlight_line(self.AQ),
                update_info(r"$\therefore AP\,=\,AQ$"),
                Wait(1),
                
                dehighlight_line(self.AP),
                dehighlight_line(self.AQ),
                highlight_line(self.PQ),
                highlight_line(self.BC),
                highlight_line(self.CA),
                highlight_line(self.AP),
                update_info(r"又$\because PQ=BC=AC=AP$"),
                Wait(1.5),
                
                dehighlight_line(self.PQ),
                dehighlight_line(self.BC),
                dehighlight_line(self.CA),
                dehighlight_line(self.AP),
                Create(self.trAPQ),
                update_info(r"$\therefore \triangle APQ$ 是等边三角形"),
                Wait(1.5),
                
                FadeOut(self.trAPQ),
                Wait(0.5),
                
                handle_angle(self.P, self.AP, self.PQ, GREEN), 
                update_info(r"$\therefore \angle APQ\,=\,60^\circ$"),
                Wait(1.5),
                update_info(r"$\therefore \angle 2 - \angle 1\,=\,60^\circ$"),
                Wait(1.5)
            )
            
            self.play(update_info(r"""$\begin{cases}
            \angle 1 + \angle 2\,=\,90^\circ \\
            \angle 2 - \angle 1\,=\,60^\circ
            \end{cases}$"""))
            self.wait(2) # 增加等待，让观众有时间看方程组
            self.play(update_info(r"""解得 $\begin{cases}
            \angle 1\,=\,15^\circ \\
            \angle 2\,=\,75^\circ
            \end{cases}$"""))
            self.wait(2) # 增加等待，让观众有时间看结果

            self.play(update_info(r"$\therefore \angle BCP\,=\,15^\circ$"))
            self.wait(2)
        
        def solution2():
            # 方法二：补全正方形 + 全等三角形
            reset_scene("方法二")
            
            # 三角形DBP填充（方法二专用）
            trDBP = Polygon(
                self.D.get_center(),
                self.B.get_center(),
                self.P.get_center(),
                color=GREEN,
                fill_opacity=0.3,
                stroke_width=2
            )
            # 三角形ADP填充（方法二专用）
            trADP = Polygon(
                self.A.get_center(),
                self.D.get_center(),
                self.P.get_center(),
                color=BLUE,
                fill_opacity=0.3,
                stroke_width=2
            )
            
            # 标注∠1 ∠2，补全正方形
            self.play(
                Create(self.sec1),
                Create(self.lsec1),
                Wait(1),
                
                Create(self.sec2),
                Create(self.lsec2),
                Wait(1),
                
                Create(self.D),
                Write(self.lD),
                Create(self.DB),
                Create(self.DA),
                update_info(r"作 $DA \equalparallel BC,\ DB \equalparallel AC$"),
                Wait(1.5),
                
                Create(self.DP),
                update_info(r"连接 $DP$"),
                Wait(1),
                
                handle_angle(self.A, self.DA, self.CA, ORANGE),
                update_info(r"$\therefore \angle DAC = 180^\circ - \angle ACB = 90^\circ$"),
                Wait(1.5),
                
                dehighlight_angle(self.A, self.DA, self.CA),
                update_info(r"$\because \angle ACB = 90^\circ$"),
                Wait(1),
                
                update_info(r"$\therefore \angle 1 = 90^\circ - \angle 2$"),
                Wait(1.5),
                
                highlight_line(self.AP),
                highlight_line(self.CA),
                update_info(r"$\because AP = AC$"),
                Wait(1),
                
                dehighlight_line(self.AP),
                dehighlight_line(self.CA),
                Create(self.trAPC),
                update_info(r"$\therefore \triangle APC$ 为等腰三角形"),
                Wait(1.5),
                
                FadeOut(self.trAPC),
                handle_angle(self.A, self.AP, self.CA, YELLOW),
                update_info(r"$\therefore \angle PAC = 180^\circ - 2\angle 2 = 2\angle 1$"),
                Wait(2),
                
                dehighlight_angle(self.A, self.AP, self.CA)
            )
            
            # 全等三角形证明
            self.play(
                highlight_line(self.DB),
                highlight_line(self.CA),
                update_info(r"在 $\triangle DBP$ 和 $\triangle ACP$ 中"),
                Wait(1),
                
                update_info(r"$DB = AC$"),
                Wait(1),
                
                dehighlight_line(self.DB),
                dehighlight_line(self.CA),
                
                handle_angle(self.B, self.DB, self.PB, GREEN),
                update_info(r"$\angle DBP = \angle ACP$"),
                Wait(1.5),
                
                dehighlight_angle(self.B, self.DB, self.PB),
                
                highlight_line(self.PB),
                highlight_line(self.PC),
                update_info(r"$BP = PC$"),
                Wait(1),
                
                dehighlight_line(self.PB),
                dehighlight_line(self.PC),
                
                Create(trDBP),
                Create(self.trAPC),
                update_info(r"$\therefore \triangle DBP \cong \triangle ACP\ (SAS)$"),
                Wait(2),
                
                FadeOut(trDBP),
                FadeOut(self.trAPC),
                
                highlight_line(self.DP),
                highlight_line(self.AP),
                update_info(r"$\therefore DP = AP$"),
                Wait(1),
                
                dehighlight_line(self.DP),
                dehighlight_line(self.AP),
                
                highlight_line(self.DA),
                highlight_line(self.BC),
                highlight_line(self.CA),
                highlight_line(self.AP),
                update_info(r"又 $\because DA = BC = AC = AP$"),
                Wait(1.5),
                
                dehighlight_line(self.DA),
                dehighlight_line(self.BC),
                dehighlight_line(self.CA),
                dehighlight_line(self.AP),
                
                Create(trADP),
                update_info(r"$\therefore \triangle ADP$ 为等边三角形"),
                Wait(1.5),
                
                FadeOut(trADP),
                
                handle_angle(self.A, self.AP, self.DA, GREEN),
                update_info(r"$\therefore \angle PAD = 60^\circ$"),
                Wait(1.5),
                
                dehighlight_angle(self.A, self.AP, self.DA),
                handle_angle(self.A, self.DA, self.CA, ORANGE),
                update_info(r"又 $\because \angle PAD + \angle PAC = \angle DAC = 90^\circ$"),
                Wait(2),
                
                dehighlight_angle(self.A, self.DA, self.CA),
                update_info(r"$\therefore 60^\circ + 2\angle 1 = 90^\circ$"),
                Wait(1.5),
                
                update_info(r"解得 $\angle 1 = 15^\circ$"),
                Wait(1.5),
                
                Create(self.PCB),
                Write(self.lPCB),
                update_info(r"即 $\angle BCP = 15^\circ$")
            )
            self.wait(2)
        
        def solution3():
            reset_scene("方法三")
            
            infos = [
                r"$\therefore \sqrt{(-k-x)^2+y^2}=\sqrt{x^2+y^2}$",
                r"$(-k-x)^2+y^2=x^2+y^2$",
                r"$k^2+2xk+x^2=x^2$",
                r"$-2xk=k^2 $",
                r"$-2x=k$",
                r"$x=-\frac{k}{2}$"
            ]
            
            infos2 = [
                r"$\therefore \sqrt{x^2+(k-y)^2}=\sqrt{k^2}$",
                r"$x^2+(k-y)^2=k^2$",
                r"$(-\frac{k}{2})^2+(k-y)^2=k^2$",
                r"$\frac{k^2}{4}+k^2-2ky+y^2=k^2$",
                r"$y^2-2ky+\frac{k^2}{4}=0$",
                r"$\Delta=(-2k)^2-4\times1\times\frac{k^2}{4}$",
                r"$\Delta=3k^2$",
                r"$y_{1,\,2}=\frac{-(-2k)\pm\sqrt{\Delta}}{2\times1}$",
                r"$y_{1,\,2}=\frac{2k\pm k\sqrt{3}}{2}$",
                r"$y_1=\frac{2k+k\sqrt{3}}{2},\,y_2=\frac{2k-k\sqrt{3}}{2}$",
                r"$y_1=k+\frac{\sqrt{3}k}{2}>k$, 舍去",
                r"$y=\frac{2k-k\sqrt{3}}{2}$"
            ]
            
            self.play (
                Wait(2),
                
                Create(self.ax), update_info(r"以 $C$ 为原点建立直角坐标系"),
                Wait(1.5),
                
                update_info(r"设 $\triangle ABC$ 直角边长度为 $k\,(k > 0)$"),
                Create(create_label(self.CA, RIGHT, "$k$", use_tex=True)),
                Create(create_label(self.BC, DOWN, "$k$", use_tex=True)),
                Wait(1.5),
                
                update_info(r"""则 $\begin{cases}
A\,(0,\,k) \\
B\,(-k,\,0) \\
C\,(0,\,0)
\end{cases}$"""),
                Transform(self.lA, create_label(self.A, UP + RIGHT, r"A\,$(0,\,k)$", use_tex=True)),
                Transform(self.lB, create_label(self.B, LEFT + UP, r"$B\,(-k,\,0)$", use_tex=True)),
                Transform(self.lC, create_label(self.C, RIGHT + UP, r"$C\,(0,\,0)$", use_tex=True)),
                Wait(1.5),
                
                update_info(r"设 $P\,(x,\,y)$"),
                Transform(self.lP, create_label(self.P, UP, r"P\,$(x,\,y)$", use_tex=True)),
                highlight_line(self.PB),
                highlight_line(self.PC),
                update_info(r"$\because BP=PC$"),
                Wait(1),
                
                dehighlight_line(self.PB),
                dehighlight_line(self.PC)
            )
            
            for info in infos:
                self.play(update_info(info))
                self.wait(1)
                
            self.play(
                Transform(self.lP, create_label(self.P, UP, r"$P\,(-\frac{k}{2},\,y)$", use_tex=True)),
                update_info(r"$\therefore P\,(-\frac{k}{2},\,y)$"),
                Wait(0.5),
                
                highlight_line(self.AP),
                highlight_line(self.CA),
                update_info(r"$\because AP=AC$"),
                Wait(1),
                
                dehighlight_line(self.AP),
                dehighlight_line(self.CA)
            )
            for info in infos2:
                self.play(update_info(info))
                self.wait(1)
            self.play(
                Transform(self.lP, create_label(self.P, UP, r"$P\,(-\frac{k}{2},\,\frac{2k-k\sqrt{3}}{2})$", use_tex=True)),
                update_info(r"$\therefore P\,(-\frac{k}{2},\,\frac{2k-k\sqrt{3}}{2})$"),
                
                Wait(1.5),
                update_info(r"$\therefore \tan \angle PCB = \frac{\frac{2k-k\sqrt{3}}{2}}{-\frac{k}{2}} = 2-\sqrt{3}$"),
                
                Wait(1.5),
                Create(self.PCB),
                Write(self.lPCB),
                update_info(r"$\therefore \angle PCB=15^\circ$")
            )
            self.wait(2)
        
        def show_all_solutions():
            """结尾依次展示三个方法的完整版"""
            self.wait(1)
            self.play(update_info(""))
            self.clear()
            
            # 标题
            title = Text("三种方法完整版", font_size=40)
            self.play(Write(title))
            self.wait(1.5)
            self.play(FadeOut(title))
            
            # 方法一完整版
            summary1 = Tex(r"""
            $\begin{aligned}
            &\textbf{方法一：辅助线 } PQ \\
            &\text{作 } PQ \equalparallel BC,\ \text{连接 } AQ, CQ \\
            &\because PQ \parallel BC \therefore \angle QPC = \angle 1 \\
            &\because AP = AC \therefore \triangle APC \text{ 为等腰三角形} \\
            &\therefore \angle APC = \angle 2,\ \angle APQ = \angle 2 - \angle 1 \\
            &\because \angle ACB = 90^\circ \therefore \angle 1 + \angle 2 = 90^\circ \\
            &\because PQ = BC = AC = AP \therefore AP = AQ \\
            &\therefore \triangle APQ \text{ 是等边三角形} \therefore \angle APQ = 60^\circ \\
            &\therefore \angle 2 - \angle 1 = 60^\circ \\
            &\text{联立得 } \angle 1 = 15^\circ \\
            &\therefore \angle BCP = 15^\circ
            \end{aligned}$
            """, font_size=22, tex_template=CtexTemplate())
            self.play(Write(summary1))
            self.wait(5)
            self.play(FadeOut(summary1))
            self.wait(0.5)
            
            # 方法二完整版
            summary2 = Tex(r"""
            $\begin{aligned}
            &\textbf{方法二：补全正方形} \\
            &\text{作 } DA \equalparallel BC,\ DB \equalparallel AC \\
            &\therefore \angle DAC = 180^\circ - \angle ACB = 90^\circ \\
            &\because \angle ACB = 90^\circ \therefore \angle 1 = 90^\circ - \angle 2 \\
            &\because AP = AC \therefore \triangle APC \text{ 为等腰三角形} \\
            &\therefore \angle PAC = 180^\circ - 2\angle 2 = 2\angle 1 \\
            &\text{在 } \triangle DBP \text{ 和 } \triangle ACP \text{ 中：} \\
            &\quad DB = AC,\ \angle DBP = \angle ACP,\ BP = PC \\
            &\therefore \triangle DBP \cong \triangle ACP\ (SAS) \\
            &\therefore DP = AP \\
            &\text{又 } DA = BC = AC = AP \\
            &\therefore \triangle ADP \text{ 为等边三角形} \therefore \angle PAD = 60^\circ \\
            &\text{又 } \angle PAD + \angle PAC = \angle DAC = 90^\circ \\
            &\therefore 60^\circ + 2\angle 1 = 90^\circ \therefore \angle 1 = 15^\circ \\
            &\text{即 } \angle BCP = 15^\circ
            \end{aligned}$
            """, font_size=22, tex_template=CtexTemplate())
            self.play(Write(summary2))
            self.wait(5)
            self.play(FadeOut(summary2))
            self.wait(0.5)
            
            # 方法三完整版
            summary3 = Tex(r"""
            $\begin{aligned}
            &\textbf{方法三：坐标法} \\
            &\text{以 } C \text{ 为原点建立直角坐标系，设直角边长为 } k \\
            &A(0, k),\ B(-k, 0),\ C(0, 0),\ \text{设 } P(x, y) \\
            &\because BP = PC \\
            &\therefore \sqrt{(-k-x)^2+y^2} = \sqrt{x^2+y^2} \Rightarrow x = -\frac{k}{2} \\
            &\because AP = AC \\
            &\therefore \sqrt{x^2+(k-y)^2} = k \Rightarrow y = \frac{2k - k\sqrt{3}}{2} \\
            &\therefore \tan \angle PCB = \frac{y}{|x|} = 2 - \sqrt{3} \\
            &\therefore \angle PCB = 15^\circ
            \end{aligned}$
            """, font_size=22, tex_template=CtexTemplate())
            self.play(Write(summary3))
            self.wait(5)
            self.play(FadeOut(summary3))
            self.wait(0.5)
            
            # 谢谢观看
            thanks = Text("谢谢观看", font_size=60)
            self.play(Write(thanks))
            self.wait(3)
            self.play(FadeOut(thanks))
        
        # 3. 核心动画流程
        present_problem()
        solution1()
        solution2()
        solution3()
        show_all_solutions()