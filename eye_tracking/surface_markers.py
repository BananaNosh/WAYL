import os

import pygame


class SurfaceMarkerCreator(object):
    def __init__(self, markers=None, marker_path="player/eye_tracking/markers", marker_prefix="marker_"):
        """
        A class for drawing the given markers on the edges of a surface
        Args:
            markers(list(int|None)): the used marker numbers,
            None can be inserted if a certain edge should have less markers
            marker_path(str): the path to the marker images
            marker_prefix(str): the prefix which all markers are named with
        """
        super().__init__()

        if markers is None:
            markers = [42, 23, 11, 7]
        self.marker_paths = [os.path.join(marker_path, '{}{:02}.png'.format(marker_prefix, marker))
                             if marker is not None else None for marker in markers]

    def draw(self, game_surface, marker_size=(100, 100)):
        """
        Draws the markers on to the surface
        Args:
            game_surface(Surface): the surface to draw on
            marker_size(tuple(int, int)): the size of the drawn markers
        """
        total_markers_count = len(self.marker_paths)
        markers_count_per_edge = [(total_markers_count + 3 - i) // 4 for i in range(4)]
        for i, marker_path in enumerate(self.marker_paths):
            if marker_path is None:
                continue
            m_img = pygame.image.load(marker_path)
            pygame.transform.scale(m_img, marker_size)
            real_marker_size = m_img.get_size()
            border_x = real_marker_size[0] // 5
            border_y = real_marker_size[1] // 5

            x_left, x_right = border_x, game_surface.get_width() - real_marker_size[0] - border_x
            y_top, y_bottom = border_y, game_surface.get_height() - real_marker_size[1] - border_y

            edge = i % 4
            marker_index_at_edge = i // 4
            corner_positions = [(x_left, y_top), (x_right, y_top), (x_right, y_bottom), (x_left, y_bottom)]
            x, y = corner_positions[edge]
            if i >= 4:
                x += (corner_positions[(edge + 1) % 4][0] - corner_positions[edge][0]) \
                     // markers_count_per_edge[edge] * marker_index_at_edge
                y += (corner_positions[(edge + 1) % 4][1] - corner_positions[edge][1]) \
                     // markers_count_per_edge[edge] * marker_index_at_edge

            # draw a white background rect
            pygame.draw.rect(game_surface, (255, 255, 255),
                             [x - border_x,
                              y - border_y,
                              marker_size[0] + 2 * border_x,
                              marker_size[1] + 2 * border_y])
            # draw the marker on top of the white rect
            game_surface.blit(m_img, (x, y))
