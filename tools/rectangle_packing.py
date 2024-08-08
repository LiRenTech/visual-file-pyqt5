import math
from typing import List
from data_struct.rectangle import Rectangle
from data_struct.number_vector import NumberVector


"""
装箱问题，排序矩形
    :param rectangles: N个矩形的大小和位置
    :param margin: 矩形之间的间隔（为了美观考虑）
    :return: 调整好后的N个矩形的大小和位置，数组内每个矩形一一对应。
    例如：
    rectangles = [Rectangle(NumberVector(0, 0), 10, 10), Rectangle(NumberVector(10, 10), 1, 1)]
    这两个矩形对角放，外套矩形空隙面积过大，空间浪费，需要调整位置。

    调整后返回：

    [Rectangle(NumberVector(0, 0), 10, 10), Rectangle(NumberVector(12, 0), 1, 1)]
    参数 margin = 2
    横向放置，减少了空间浪费。
"""


def sort_rectangle_just_vertical(
    rectangles: list[Rectangle], margin: float
) -> list[Rectangle]:
    """
    仅仅将一些矩形左对齐 竖向简单排列
    这会假设外层父文件夹左上角顶点为 0 0
    O(N)
    :param rectangles:
    :param margin:
    :return:
    """
    current_y = margin

    for rectangle in rectangles:
        rectangle.location_left_top.y = current_y
        rectangle.location_left_top.x = margin
        current_y += rectangle.height + margin

    return rectangles


def sort_rectangle_fast(rectangles: list[Rectangle], margin: float) -> list[Rectangle]:
    max_width = -margin
    max_height = -margin
    putable_locs = [NumberVector(0, 0)]
    for r in rectangles:
        if max_width > max_height:
            r.location_left_top.y = max_height + margin
            r.location_left_top.x = 0
        else:
            r.location_left_top.x = max_width + margin
            r.location_left_top.y = 0
        if r.right() > max_width:
            max_width = r.right()
        if r.bottom() > max_height:
            max_height = r.bottom()
    return rectangles


def sort_rectangle_greedy(
    rectangles: list[Rectangle], margin: float
) -> list[Rectangle]:
    """
    贪心策略
    O(N^2)
    """
    if len(rectangles) == 0:
        return []

    def append_right(
        origin: Rectangle, rect: Rectangle, rects: list[Rectangle]
    ) -> Rectangle:
        ret = Rectangle(
            NumberVector(rect.location_left_top.x, rect.location_left_top.y),
            rect.width,
            rect.height,
        )
        ret.location_left_top.x = origin.right() + margin
        ret.location_left_top.y = origin.top()
        # 碰撞检测
        collision = True
        while collision:
            collision = False
            for r in rects:
                if ret.is_collision(r, margin=margin):
                    ret.location_left_top.y = r.bottom() + margin
                    ret.location_left_top.x = max(
                        ret.location_left_top.x, r.right() + margin
                    )
                    collision = True
                    break
        return ret

    def append_bottom(
        origin: Rectangle, rect: Rectangle, rects: list[Rectangle]
    ) -> Rectangle:
        ret = Rectangle(
            NumberVector(rect.location_left_top.x, rect.location_left_top.y),
            rect.width,
            rect.height,
        )
        ret.location_left_top.y = origin.bottom() + margin
        ret.location_left_top.x = origin.left()
        # 碰撞检测
        collision = True
        while collision:
            collision = False
            for r in rects:
                if ret.is_collision(r, margin=margin):
                    ret.location_left_top.x = r.right() + margin
                    ret.location_left_top.y = max(
                        ret.location_left_top.y, r.bottom() + margin
                    )
                    collision = True
                    break
        return ret

    rectangles[0].location_left_top.x = 0
    rectangles[0].location_left_top.y = 0
    ret = [rectangles[0]]
    width = rectangles[0].width
    height = rectangles[0].height
    for i in range(1, len(rectangles)):
        min_space_score = -1
        min_shape_score = -1
        min_rect = None
        for j in range(len(ret)):
            r = append_right(ret[j], rectangles[i], ret)
            space_score = r.right() - width + r.bottom() - height
            shape_score = abs(max(r.right(), width) - max(r.bottom(), height))
            if (
                min_space_score == -1
                or space_score < min_space_score
                or (space_score == min_space_score and shape_score < min_shape_score)
            ):
                min_space_score = space_score
                min_shape_score = shape_score
                min_rect = r
            r = append_bottom(ret[j], rectangles[i], ret)
            space_score = r.right() - width + r.bottom() - height
            shape_score = abs(max(r.right(), width) - max(r.bottom(), height))
            if (
                min_space_score == -1
                or space_score < min_space_score
                or (space_score == min_space_score and shape_score < min_shape_score)
            ):
                min_space_score = space_score
                min_shape_score = shape_score
                min_rect = r
        width = max(width, r.right())
        height = max(height, r.bottom())
        assert min_rect is not None
        ret.append(min_rect)

    return ret


def sort_rectangle_many_files_less_folders(
    rectangles: List[Rectangle], margin: float
) -> list[Rectangle]:
    """
    多文件,少文件夹的情况
    文件夹排在左上角，只拍成一行
    文件另起一行以矩阵形式排列
    """
    # 如何判定一个文件是文件夹还是文件？矩形的高度=100是文件，>100是文件夹
    files = [r for r in rectangles if r.height <= 100]
    folders = [r for r in rectangles if r.height > 100]
    files = sort_rectangle_all_files(files, margin)
    folders = sort_rectangle_all_files(folders, margin)
    # 找到文件夹列表中最靠左下角的那个文件夹矩形的左下角坐标
    min_x = min(folders, key=lambda r: r.location_left_top.x).location_left_top.x
    
    max_bottom_folder = max(folders, key=lambda r: r.bottom())

    max_y = max_bottom_folder.bottom() + margin
    for file in files:
        file.location_left_top.x += min_x
        file.location_left_top.y += max_y
    # 看似没排，其实是排好了
    return rectangles
    pass

def sort_rectangle_all_files(
    rectangles: List[Rectangle], margin: float
) -> list[Rectangle]:
    """
    专门解决一个文件夹里面全都是小文件的情况的矩形摆放位置的情况。
    注：这种情况只适用于全是文件，没有文件夹的情况。
    """
    if len(rectangles) == 0:
        return []

    # 先找到所有矩形中最宽的矩形宽度
    max_width = 0
    for r in rectangles:
        if r.width > max_width:
            max_width = r.width

    # 再找到所有矩形中最高的矩形高度
    max_height = 0
    for r in rectangles:
        if r.height > max_height:
            max_height = r.height

    # 假设按照正方形摆放，不管宽高比例，边上的数量
    count_in_side = math.ceil(len(rectangles) ** 0.5)
    y_index = 0
    x_index = 0

    for rectangle in rectangles:
        if x_index > count_in_side - 1:
            x_index = 0
            y_index += 1
        rectangle.location_left_top.x = x_index * (max_width + margin)
        rectangle.location_left_top.y = y_index * (max_height + margin)
        x_index += 1

    return rectangles


def sort_rectangle_right_bottom(
    rectangles: list[Rectangle], margin: float
) -> list[Rectangle]:
    """不停的往右下角放的策略"""

    def append_right(
        origin: Rectangle, rect: Rectangle, rects: list[Rectangle]
    ) -> None:
        rect.location_left_top.x = origin.right() + margin
        rect.location_left_top.y = origin.top()
        # 碰撞检测
        collision = True
        while collision:
            collision = False
            for r in rects:
                if rect.is_collision(r):
                    rect.location_left_top.y = r.bottom() + margin
                    collision = True
                    break

    def append_bottom(
        origin: Rectangle, rect: Rectangle, rects: list[Rectangle]
    ) -> None:
        rect.location_left_top.y = origin.bottom() + margin
        rect.location_left_top.x = origin.left()
        # 碰撞检测
        collision = True
        while collision:
            collision = False
            for r in rects:
                if rect.is_collision(r):
                    rect.location_left_top.x = r.right() + margin
                    collision = True
                    break

    rectangles[0].location_left_top.x = 0
    rectangles[0].location_left_top.y = 0
    ret = [rectangles[0]]
    width = rectangles[0].width
    height = rectangles[0].height
    index = 0
    for i in range(1, len(rectangles)):
        if width < height:
            append_right(rectangles[index], rectangles[i], ret)
            w = rectangles[i].right()
            if w > width:
                width = w
                index = i
        else:
            append_bottom(rectangles[index], rectangles[i], ret)
            h = rectangles[i].bottom()
            if h > height:
                height = h
                index = i
        ret.append(rectangles[i])

    return ret
