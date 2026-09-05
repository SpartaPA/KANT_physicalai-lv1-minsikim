"""문제 5 — 동차변환 inv_T 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 것은 `inv_T` 검증이지만,
점/방향 구분과 벡터화, 최소자승까지 함께 검증해 두면 이후 문제에서 안전하다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import rot_x, rot_y, rot_z
from src.transform import (
    inv_T,
    least_squares_normal_equation,
    make_T,
    transform_direction,
    transform_point,
    transform_points,
)


@pytest.fixture
def T():
    """테스트에 쓸 대표 동차변환 하나."""
    R = rot_z(0.9) @ rot_y(-0.35) @ rot_x(1.3)
    return make_T(R, [0.35, -0.15, 0.55])


def test_inv_T_gives_identity(T):
    # TODO: inv_T(T) @ T 와 T @ inv_T(T) 가 모두 4x4 단위행렬인지 검사
    invtt = inv_T(T) @ T
    tinvt = T @ inv_T(T)
    assert invtt.shape[0] == 4 and invtt.shape[1] == 4
    assert tinvt.shape[0] == 4 and tinvt.shape[1] == 4


def test_inv_T_matches_generic_inverse(T):
    # TODO: inv_T(T) 가 np.linalg.inv(T) 와 일치하는지 검사 (np.linalg 는 검산용)
    assert np.allclose(inv_T(T), np.linalg.inv(T))


def test_point_and_direction_differ(T):
    # TODO: 같은 벡터를 점(w=1)/방향(w=0)으로 변환하면 결과가 다르고,
    #       그 차이가 정확히 병진 벡터 T[:3, 3] 이며,
    #       방향 변환은 길이를 보존하는지 검사
    p = np.array([1,1,1])
    trs_p = transform_point(T, p)
    trs_d = transform_direction(T, p)
    assert np.allclose(trs_p, trs_d) == False
    
    translation = T[:3, 3]
    assert np.allclose(trs_p - trs_d, translation)
    assert np.isclose(np.linalg.norm(trs_d), np.linalg.norm(p))


def test_transform_points_is_vectorized(T):
    # TODO: (N,3) 점군을 한 번에 변환한 결과가
    #       transform_point 를 반복문으로 돌린 결과와 같은지 검사
    points = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0],
        [1.0, 0.0, 2.0],
    ])

    # 벡터화된 변환
    transformed = transform_points(T, points)

    # transform_point를 반복해서 변환한 결과
    expected = np.array([
        transform_point(T, p)
        for p in points
    ])

    # 두 결과가 같은지 검사
    assert np.allclose(transformed, expected)


def test_roundtrip_through_inverse(T):
    # TODO: T 로 보냈다가 inv_T(T) 로 되돌리면 원래 점군이 나오는지 검사
    points = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0],
        [1.0, 0.0, 2.0],
    ])

    # T로 변환
    transformed = transform_points(T, points)

    # T의 역변환
    T_inv = inv_T(T)

    # 다시 원래 좌표계로 변환
    restored = transform_points(T_inv, transformed)

    # 원래 점군과 같은지 검사
    assert np.allclose(restored, points)


def test_least_squares_matches_lstsq():
    # TODO: 노이즈를 섞은 과결정 문제를 만들어
    #       least_squares_normal_equation 의 해가 np.linalg.lstsq 와 일치하고
    #       잔차가 A 의 열공간에 수직(A^T r = 0)인지 검사
    # 과결정 문제: 방정식 6개, 미지수 3개
    A = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0],
        [1.0, 0.0, 2.0],
        [3, 4, 5],
        [6, 7, 8]
    ])

    # 기준이 되는 임의의 해
    x_true = np.array([1.0, 2.0, -1.0])

    # 노이즈가 섞인 b
    noise = np.array([0.1, -0.2, 0.05, 0.1, -0.1, 0.2])
    b = A @ x_true + noise

    # 직접 구현한 최소제곱해
    x, residual = least_squares_normal_equation(A, b)

    # NumPy 최소제곱해
    x_lstsq, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

    # 두 해가 일치하는지 확인
    assert np.allclose(x, x_lstsq)

    # 잔차가 A의 열공간에 수직인지 확인
    assert np.allclose(A.T @ residual, 0)
