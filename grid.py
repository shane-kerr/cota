from items import Item
import textui

FLOOR_COLOR = (textui.WHITE, textui.BLACK, textui.NORMAL)
WALL_COLOR = (textui.WHITE, textui.BLACK, textui.BOLD)
DOOR_COLOR = (textui.YELLOW, textui.BLACK, textui.NORMAL)
DARK_COLOR = (textui.BLACK, textui.BLACK, textui.NORMAL)
MEMORY_COLOR = (textui.BLACK, textui.BLACK, textui.BOLD)

class Square:
    def __init__(self):
        self.stuff = [ ]
    def view(self):
        if self.stuff:
            return self.stuff[-1].view()
        else:
            return ('.', FLOOR_COLOR)
    def drop(self, thing):
        assert(isinstance(thing, Item))
        self.stuff.append(thing)
    def pickup(self, thing):
        self.stuff.remove(thing)
    def isempty(self):
        return len(self.stuff) == 0
    def istransparent(self):
        for thing in self.stuff:
            if not thing.transparent:
                return False
        return True
    def isblocked(self):
        for thing in self.stuff:
            if thing.blocking:
                return True
        return False
    def stuff_uniq_ids(self):
        stuff_list = [ ]
        for thing in self.stuff:
            stuff_list.append(thing.uniq_id)
        return stuff_list
    
class Map:
    def __init__(self, width, height, items):
        self.width = width
        self.height = height
        self.grid = [ ]
        self.items = items

        # create our empty map
        for col in range(width):
            new_col = [ ]
            for row in range(height):
                new_col.append(Square())
            self.grid.append(new_col)

    def enclose(self):
        wall = Item('#', WALL_COLOR)

        # put some walls around the outer edge
        for col in range(self.width):
            self.drop_item_at(self.items.copy_item(wall), col, 0)
            self.drop_item_at(self.items.copy_item(wall), col, self.height-1)
        for row in range(1, self.height-1):
            self.drop_item_at(self.items.copy_item(wall), 0, row)
            self.drop_item_at(self.items.copy_item(wall), self.width-1, row)

    def dump(self):
        dump = [ ]
        for x in range(self.width):
            for y in range(self.height):
                info = {
                    "x": x,
                    "y": y,
                    "stuff": self.grid[col][row].stuff_uniq_ids(),
                }
                dump.append(info)
        return { "width": self.width, "height": self.height,
                 "map_dump": dump }

    def drop_item_at(self, item, x, y):
        self.grid[x][y].drop(item)
        item.pos = (x, y)

    def pickup_item(self, item):
        self.grid[item.pos[0]][item.pos[1]].pickup(item)
        item.pos = None

    def can_move_onto(self, x, y):
        return not self.grid[x][y].isblocked()

    def can_see_through(self, x, y):
        return self.grid[x][y].istransparent()

    # quadrants
    # \6|2/
    # 5\|/1
    # --+--
    # 7/|\3
    # /8|4\
    # http://en.literateprograms.org/Bresenham%27s_line_algorithm_%28Python%29
    def is_los(self, x0, y0, x1, y1):
        # init
        deltax = abs(x1 - x0)
        deltay = abs(y1 - y0)
        error = 0
        # quadrants 1,2,3,4
        if x1 >= x0:
            # quadrants 1,2
            if y1 >= y0:
                # quadrant 1
                if (x1 - x0) >= (y1 - y0):
                    y = y0
                    # core loop
                    for x in range(x0, x1):
                        if not self.can_see_through(x, y):
                            return False
                        error = error + deltay
                        if (error << 1) >= deltax:
                            y = y + 1
                            error = error - deltax
                # quadrant 2
                else:
                    x = x0
                    # core loop
                    for y in range(y0, y1):
                        if not self.can_see_through(x, y):
                            return False
                        error = error + deltax
                        if (error << 1) >= deltay:
                            x = x + 1
                            error = error - deltay
            # quadrants 3,4
            else:
                # quadrant 3
                if (x1 - x0) >= (y0 - y1):
                    y = y0
                    # core loop
                    for x in range(x0, x1):
                        if not self.can_see_through(x, y):
                            return False
                        error = error + deltay
                        if (error << 1) >= deltax:
                            y = y - 1
                            error = error - deltax
                # quadrant 4
                else:
                    x = x0
                    # core loop
                    for y in range(y0, y1, -1):
                        if not self.can_see_through(x, y):
                            return False
                        error = error + deltax
                        if (error << 1) >= deltay:
                            x = x + 1
                            error = error - deltay
        # quadrants 5,6,7,8
        else:
            # quadrants 5,6
            if y1 >= y0:
                # quadrant 5
                if (x0 - x1) >= (y1 - y0):
                    y = y0
                    # core loop
                    for x in range(x0, x1, -1):
                        if not self.can_see_through(x, y):
                            return False
                        error = error + deltay
                        if (error << 1) >= deltax:
                            y = y + 1
                            error = error - deltax
                # quadrant 6
                else:
                    x = x0
                    # core loop
                    for y in range(y0, y1):
                        if not self.can_see_through(x, y):
                            return False
                        error = error + deltax
                        if (error << 1) >= deltay:
                            x = x - 1
                            error = error - deltay
            # quadrants 7,8
            else:
                # quadrant 7
                if (x0 - x1) >= (y0 - y1):
                    y = y0
                    # core loop
                    for x in range(x0, x1, -1):
                        if not self.can_see_through(x, y):
                            return False
                        error = error + deltay
                        if (error << 1) >= deltax:
                            y = y - 1
                            error = error - deltax
                # quadrant 8
                else:
                    x = x0
                    # core loop
                    for y in range(y0, y1, -1):
                        if not self.can_see_through(x, y):
                            return False
                        error = error + deltax
                        if (error << 1) >= deltay:
                            x = x - 1
                            error = error - deltay
        return True

    def is_los_symmetric(self, x0, y0, x1, y1):
        return self.is_los(x0, y0, x1, y1) or self.is_los(x1, y1, x0, y0)

    def view(self, center_x, center_y, view_width, view_height, r):
        nowhere = (' ', DARK_COLOR)
        assert((view_height & 1) == 1)
        assert((view_width & 1) == 1)
        half_wide = view_width // 2
        half_high = view_height // 2
# these asserts mean that we can't show all the visible area
#        assert((half_high <= r)
#        assert((half_wide <= r)
        r_squared = abs(r) * (abs(r) + 1)
        v = [ ]
        for x in range(view_width):
            map_x = x - half_wide + center_x
            if (map_x < 0) or (map_x >= self.width):
                view_col = [ nowhere ] * view_height
            else:
                view_col = [ ]
                for y in range(view_height):
                    map_y = y - half_high + center_y
                    if (map_y < 0) or (map_y >= self.height):
                        view_col.append(nowhere)
                    else:
                        square_view = self.grid[map_x][map_y].view()
                        x_dist = abs(half_wide - x)
                        y_dist = abs(half_high - y)
                        dist_squared = y_dist*y_dist + x_dist*x_dist
                        if (dist_squared > r_squared) or \
                            not self.is_los_symmetric(center_x, center_y, 
                                                      map_x, map_y):
                            view_col.append(nowhere)
                        else:
                            view_col.append(square_view)
            v.append(view_col)
        return v

class MapMemory:
    def __init__(self, m):
        self.m = m
        self.grid = [ ]
        nowhere = (' ', DARK_COLOR)
        for col in range(m.width):
            new_col = [ ]
            for row in range(m.height):
                new_col.append(nowhere)
            self.grid.append(new_col)


    def add_view(self, x, y, view):
        nowhere = (' ', DARK_COLOR)
        for col in range(len(view)):
            for row in range(len(view[0])):
                square = view[col][row]
                if square != nowhere:
                    self.grid[x+col][y+row] = square

    def read_memory(self, x0, y0, x1, y1):
        wide = x1 - x0 + 1
        high = y1 - y0 + 1
        nowhere = (' ', DARK_COLOR)
        nowhere_col = [ nowhere, ] * high
        view = []
        for x in range(x0, 0):
            view.append(nowhere_col)
        for x in range(max(x0, 0), min(x1+1, self.m.width)):
            if y0 < 0:
                col = [ nowhere, ] * -y0
            else:
                col = [ ]
            col.extend(self.grid[x][max(y0, 0):min(y1+1, self.m.height)])
            if y1 >= self.m.height:
                col.extend([ nowhere, ] * (y1 - self.m.height + 1))
            view.append(col)
        for x in range(self.m.width-1, x1):
            view.append(nowhere_col)
        return view

#    def update_memory(self, view, x_add, y_add, x0, y0, x1, y1):
#        # XXX: need to remove this
#        self.add_view(x_add, y_add, view)
#        x0_view = x_add
#        y0_view = y_add
#        x1_view = x0_view + len(view) - 1
#        y1_view = y0_view + len(view[0]) - 1
#        # get our old view
#        new_view = self.read_memory(x0, y0, x1, y1)
#        # now go through and every place that we cannot currently see
#        # change the color to a dark gray
#        nowhere = (' ', DARK_COLOR)
#        x_ofs = 0
#        for x in range(x0, x1+1):
#            y_ofs = 0
#            for y in range(y0, y1+1):
#                if (x >= x0_view) and (x <= x1_view) and \
#                   (y >= y0_view) and (y <= y1_view):
#                    square = view[x-x0_view][y-y0_view]
#                    if square == nowhere:
#                        new_view[x_ofs][y_ofs] = (new_view[x_ofs][y_ofs][0], 
#                                                  MEMORY_COLOR)
#                else:
#                    new_view[x_ofs][y_ofs] = (new_view[x_ofs][y_ofs][0], 
#                                              MEMORY_COLOR)
#                y_ofs = y_ofs + 1
#            x_ofs = x_ofs + 1
#        return new_view

    def look_at(self, x0, y0, x1, y1, r):
        wid = x1 - x0 + 1
        assert(wid & 1)
        hig = y1 - y0 + 1
        assert(wid & 1)
        x_center = (x1 + x0) // 2
        y_center = (y1 + y0) // 2
        view = self.m.view(x_center, y_center, wid, hig, r)
        nowhere = (' ', DARK_COLOR)
        for x in range(max(x0, 0), min(x1+1, self.m.width)):
            for y in range(max(y0, 0), min(y1+1, self.m.height)):
                square = view[x-x0][y-y0]
                if square != nowhere:
                    # if the square is visible, copy to our memory
                    self.grid[x][y] = square
                else:
                    # if the square is not visible, update the view from memory
                    view[x-x0][y-y0] = (self.grid[x][y][0], MEMORY_COLOR)
        return view
