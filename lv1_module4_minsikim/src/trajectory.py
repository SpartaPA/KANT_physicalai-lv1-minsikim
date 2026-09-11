"""문제 4 — 궤적 보간. (학생 작성용 템플릿)

경유점(waypoint)을 지나는 궤적을 선형 보간 / 큐빅 스플라인으로 만들고,
시작·끝에서 속도와 가속도가 0 이 되는 5차 다항식 프로파일을 구현한다.

입력 규약
--------
- t_wp : (M,) 경유점 시각, 오름차순
- q_wp : (M,) 스칼라 궤적 또는 (M, D) 다차원 궤적 (예: 3차원 위치는 D = 3)
- t    : (N,) 평가할 시각 (t_wp[0] <= t <= t_wp[-1])
- 반환 : q_wp 가 (M,) 이면 (N,), (M, D) 이면 (N, D)

큐빅 스플라인은 `scipy.interpolate.CubicSpline` 을 써도 된다 (axis=0).
"""

from __future__ import annotations

import numpy as np
import scipy

__all__ = ["linear_interp", "cubic_spline_interp", "quintic_profile", "finite_diff"]


def linear_interp(t_wp, q_wp, t) -> np.ndarray:
    """경유점 사이를 직선으로 잇는 보간. 각 차원마다 `np.interp` 를 쓰면 된다.

    위치는 이어지지만 경유점에서 속도가 불연속(꺾임)이다.
    """
    # TODO: 문제 4-1
    t_wp = np.asarray(t_wp, dtype=float)
    q_wp = np.asarray(q_wp, dtype=float)
    t = np.asarray(t, dtype=float)

    if q_wp.ndim == 1:
        return np.interp(t, t_wp, q_wp)
    
    # (N, D) 형태의 다차원 입력 처리 (열 독립 보간)
    D = q_wp.shape[1]
    res = np.zeros((len(t), D))
    for k in range(D):
        res[:, k] = np.interp(t, t_wp, q_wp[:, k])
    return res


def cubic_spline_interp(t_wp, q_wp, t, bc_type: str = "natural") -> np.ndarray:
    """경유점을 지나는 큐빅 스플라인 보간 (위치·속도·가속도가 모두 연속, C2).

    bc_type : 양끝 경계 조건. "natural" (양끝 가속도 0) 또는 "clamped" (양끝 속도 0).
    """
    # TODO: 문제 4-1
    t_wp = np.asarray(t_wp, dtype=float)
    q_wp = np.asarray(q_wp, dtype=float)
    t = np.asarray(t, dtype=float)

    # SciPy의 CubicSpline은 axis=0 지정을 통해 다차원 배열 보간을 지원함
    cs = scipy.interpolate.CubicSpline(t_wp, q_wp, axis=0, bc_type=bc_type)
    return cs(t)


def quintic_profile(t, t0: float, tf: float, q0, qf,
                    v0=0.0, vf=0.0, a0=0.0, af=0.0):
    """5차 다항식 궤적 q(t) 와 그 도함수 (q, qd, qdd) 를 돌려준다.

    경계 조건 6개 — q(t0)=q0, q(tf)=qf, qd(t0)=v0, qd(tf)=vf, qdd(t0)=a0, qdd(tf)=af —
    로 계수 6개 (c0 ~ c5) 를 정한다. 경계 속도·가속도가 모두 0 인 기본형은

        tau = (t - t0) / (tf - t0)
        s(tau) = 10 tau^3 - 15 tau^4 + 6 tau^5
        q(t) = q0 + (qf - q0) s(tau)

    로 닫힌 꼴이 있고, 일반형은 6x6 선형계를 풀면 된다. 어느 쪽으로 구현해도 된다.
    q0, qf 가 스칼라이면 (N,), (D,) 이면 (N, D) 를 돌려준다.

    Returns
    -------
    q, qd, qdd : 위치, 속도, 가속도 (해석적 미분. 유한차분이 아니다)
    """
    # TODO: 문제 4-4
    t = np.asarray(t, dtype=float)
    q0 = np.asarray(q0, dtype=float)
    qf = np.asarray(qf, dtype=float)
    v0 = np.asarray(v0, dtype=float)
    vf = np.asarray(vf, dtype=float)
    a0 = np.asarray(a0, dtype=float)
    af = np.asarray(af, dtype=float)
    
    v0 = np.broadcast_to(v0, q0.shape)
    vf = np.broadcast_to(vf, q0.shape)
    a0 = np.broadcast_to(a0, q0.shape)
    af = np.broadcast_to(af, q0.shape)

    T = tf - t0

    # 6x6 선형계 구성
    M = np.array([
        [1, 0, 0,  0,  0,  0],
        [0, 1, 0,  0,  0,  0],
        [0, 0, 2,  0,  0,  0],
        [1, 1, 1,  1,  1,  1],
        [0, 1, 2,  3,  4,  5],
        [0, 0, 2,  6, 12, 20]
    ], dtype=float)

    # b 배열 생성: np.stack을 활용하여 0번 축 기준으로 6개의 경계조건 결합
    b = np.stack([q0, v0 * T, a0 * (T**2), qf, vf * T, af * (T**2)], axis=0)

    # 계수 c 계산: c는 (6,) 또는 (6, D)
    c = np.linalg.solve(M, b)

    tau = (t - t0) / T

    # tau 행렬 구성: (N, 6)
    tau_mat = np.column_stack([
        np.ones_like(tau),
        tau,
        tau**2,
        tau**3,
        tau**4,
        tau**5
    ])

    dtau_mat = np.column_stack([
        np.zeros_like(tau),
        np.ones_like(tau),
        2 * tau,
        3 * (tau**2),
        4 * (tau**3),
        5 * (tau**4)
    ])

    d2tau_mat = np.column_stack([
        np.zeros_like(tau),
        np.zeros_like(tau),
        2 * np.ones_like(tau),
        6 * tau,
        12 * (tau**2),
        20 * (tau**3)
    ])

    # 행렬 곱(np.matmul / @)을 이용하면 스칼라 및 (N, D) 입력에 대해 일관되게 계산됨
    q = tau_mat @ c
    qd = (dtau_mat @ c) / T
    qdd = (d2tau_mat @ c) / (T**2)

    return q, qd, qdd


def finite_diff(y, t) -> np.ndarray:
    """시간축(axis 0)에 대한 수치 미분. `np.gradient(y, t, axis=0)` 를 쓰면 된다.

    y : (N,) 또는 (N, D),  t : (N,)
    속도 = finite_diff(q, t),  가속도 = finite_diff(속도, t)
    """
    # TODO: 문제 4-2
    return np.gradient(y, t, axis=0)
