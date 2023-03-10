"""
Raytracing in 2d

This stuff is inspired by a course in MIT OpenCourseWare
18.S191 / 6.S083 / 22.S092 Introduction to Computational thinking
"""

import random
import numpy as np
import matplotlib.pyplot as plt

from photon import Photon
from typing import Optional
from interaction import Interaction
from surfaces import Surface, Mirror

# Shortcuts for typing
numeric = int | float
vec = list | np.ndarray
surface = Surface | Mirror


def create_boundaries(boundaries: tuple, reflective: bool = False) \
        -> list[surface]:
    """
    Creates the surfaces that form the rectangular edges of the geometry
    :param boundaries: Boundaries of the geometry, as a tuple of the form
    (xmin, xmax, ymin, ymax)
    :param reflective: Whether the edges are reflective or not, if not
    reflective, the photons just escape the geometry
    :return:
    """
    xmin, xmax, ymin, ymax = boundaries
    xlen = xmax - xmin
    ylen = ymax - ymin
    edge_type = Surface
    if reflective:
        edge_type = Mirror
    bottom_left = [xmin, ymin]
    bottom_right = [xmax, ymin]
    top_right = [xmax, ymax]
    top_left = [xmin, ymax]
    left_norm = [1, 0]
    bottom_norm = [0, 1]
    right_norm = [-1, 0]
    top_norm = [0, -1]
    surfs = [
        edge_type(bottom_left, bottom_norm, xlen),
        edge_type(bottom_right, right_norm, ylen),
        edge_type(top_right, top_norm, xlen),
        edge_type(top_left, left_norm, ylen)
    ]
    return surfs


def _intersect_time(p: Photon, surf: surface) -> numeric:
    """
    Calculates the time it takes for the photon to intersect the
    surface
    :param p: Photon-object
    :param surf: Some surface object
    :return:
    """
    return np.dot((surf.pos - p.pos), surf.norm) / np.dot(p.direc, surf.norm)


def _vector_len(v: vec) -> numeric:
    """
    Computes the length of the vector
    :param v:
    :return:
    """
    return np.sqrt(np.dot(v, v))


def _norm(v: vec) -> vec:
    """
    Normalizes the vector
    :param v:
    :return:
    """
    return v / _vector_len(v)


def _find_intersections(p: Photon, surf: surface) -> Optional[Interaction]:
    """
    Checks whether the photon collides with the wall
    :param p: Photon-object
    :param surf: A surface object
    :return: Either None or an Intersection-object,
    depending whether the photon collides with the wall or not
    """
    t = _intersect_time(p, surf)
    # If collision time is negative, the surface is behind the photon
    if t < 0:
        return None
    point = p.pos + t * p.direc
    dist = (point - surf.pos)
    # Check whether the collision point is actually on the surface
    if _vector_len(dist) > surf.length or np.dot(_norm(dist), surf.adj) == -1:
        return None
    # Substract a small fraction from the collision time, so that
    # the photon doesn't end up inside the wall
    point = p.pos + (t - t * 0.01) * p.direc
    return Interaction(surf, t, point)


def _closest_hit(p: Photon, surfs: list[surface]) -> Interaction:
    """
    Returns the object with which the closest collision is had, if
    any collisions occur
    :param p: A Photon object
    :param surfs: List of the surfaces present in the geometry
    :return:
    """
    hits = [_find_intersections(p, w) for w in surfs]
    hits = [h for h in hits if isinstance(h, Interaction)]
    return min(hits, key=lambda x: x.time)


def _sample_collision(p: Photon, surfs: list[surface]) -> None:
    """
    Computes the next interaction of the photon with the surfaces
    :param p:
    :param surfs:
    :return:
    """
    coll = _closest_hit(p, surfs)
    coll.surf.interact(p, coll.point)


def init_random_photons(n: int, boundaries: tuple) -> list[Photon]:
    """
    Initialize n photons with random locations and directions of travel
    :param n: Number of photons
    :param boundaries: Boundaries of the geometry, as a tuple of the form
    (xmin, xmax, ymin, ymax)
    :return:
    """
    xmin, xmax, ymin, ymax = boundaries
    photons = []
    for _ in range(n):
        x = xmin + random.random() * (xmax - xmin)
        y = ymin + random.random() * (ymax - ymin)
        direction = random.random() * np.pi * 2
        dir_vec = [np.cos(direction), np.sin(direction)]
        photons.append(Photon([x, y], dir_vec))
    return photons


def trace(p_arr: list[Photon], surfs: list[surface],
          n_events: int = 100) -> list[np.ndarray]:
    """
    Traces the paths of the photons until they escape the geometry, or
    n number of interactions have occurred
    :param p_arr: List of the photons present initially in the
    geometry
    :param surfs: List of the surfaces in the geometry
    :param n_events: Maximum number of interactions to track, so that the
    simulation doesn't run endlessly
    :return: The paths (x- and y-coordinates) of the photons
    """
    data = []
    for p in p_arr:
        coords = np.zeros((1, 2))
        coords[0] = p.pos
        for _ in range(1, n_events + 1):
            _sample_collision(p, surfs)
            coords = np.vstack((coords, p.pos))
        data.append(coords)
    return data


def plot_data(data: list[np.ndarray], **kwargs) -> None:
    """
    Plots the tracks of the photons
    :param data: List of numpy-arrays containing the coordinates
    of the photons
    :param kwargs: Keyword arguments for lineplots
    :return:
    """
    for coords in data:
        plt.scatter(coords[0, 0], coords[0, 1])
        plt.plot(coords[:, 0], coords[:, 1], **kwargs)
    plt.grid()


def main():
    xmin, xmax = -5, 5
    ymin, ymax = -5, 5
    n_photons = 2
    boundaries = (xmin, xmax, ymin, ymax)
    walls = create_boundaries(boundaries, reflective=True)
    slanted_wall = Mirror([1, 1], [0.5, 0.5], 2)
    walls.append(slanted_wall)
    photons = init_random_photons(n_photons, boundaries)
    for w in walls:
        w.plot_wall(c='red')
    data = trace(photons, walls, n_events=4)
    plot_data(data, c='blue')
    plt.show()


if __name__ == '__main__':
    main()
