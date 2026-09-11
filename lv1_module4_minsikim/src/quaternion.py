"""문제 3 — 쿼터니언 변환과 SLERP. (학생 작성용 템플릿)

규약
----
- 쿼터니언은 길이 4 배열 **(x, y, z, w)** 다. 모듈 ③ 의 `quaternion_from_axis_angle` 과
  SciPy `Rotation.as_quat()` 와 같은 순서다. w 가 스칼라(실수부)다.
- q 와 -q 는 같은 회전이다 (이중 덮개). 비교할 때는 부호를 무시하거나 |q . q_ref| 를 본다.
- 보간은 항상 **짧은 호**를 택한다: q0 . q1 < 0 이면 q1 의 부호를 뒤집고 시작한다.

SciPy 는 검산(비교) 용도로만 쓴다. 이 파일 안에서는 numpy 만 사용한다.
"""

from __future__ import annotations

import numpy as np

__all__ = ["matrix_to_quaternion", "quaternion_to_matrix", "slerp", "lerp_quat", "quat_angle"]


def matrix_to_quaternion(R) -> np.ndarray:
    """회전행렬 (3,3) -> 단위 쿼터니언 (x, y, z, w).

    권장 방법 (Shepperd): trace 가 양수이면 w 부터, 아니면 대각성분이 가장 큰 축부터 계산해
    0 으로 나누는 일을 피한다. 180도 회전(trace = -1)에서도 동작해야 한다.

        t = trace(R)
        t > 0        : s = 2 sqrt(1 + t);      w = s/4; x = (R21 - R12)/s; ...
        R00 이 최대  : s = 2 sqrt(1 + R00 - R11 - R22);  x = s/4; w = (R21 - R12)/s; ...
        (R11, R22 최대인 경우도 같은 꼴)

    반환값은 반드시 정규화하고, w >= 0 이 되도록 부호를 맞춘다 (비교가 편해진다).
    """
    # TODO: 문제 3-1
    t = np.trace(R) # 대각선 원소의 합 -> 쿼터니언 w와 밀접한 연관(1 + t = 4 w^2)
    q = np.zeros(4)

    if t > 0:
        s = 2 * np.sqrt(1 + t)

        w = s / 4
        x = (R[2, 1] - R[1, 2]) / s
        y = (R[0, 2] - R[2, 0]) / s
        z = (R[1, 0] - R[0, 1]) / s

    else:
        if R[0, 0] >= R[1, 1] and R[0, 0] >= R[2, 2]:
            # x를 먼저 계산
            s = 2 * np.sqrt(
                1 + R[0, 0] - R[1, 1] - R[2, 2]
            )

            x = s / 4
            y = (R[0, 1] + R[1, 0]) / s
            z = (R[0, 2] + R[2, 0]) / s
            w = (R[2, 1] - R[1, 2]) / s

        elif R[1, 1] >= R[2, 2]:
            # y를 먼저 계산
            s = 2 * np.sqrt(
                1 - R[0, 0] + R[1, 1] - R[2, 2]
            )

            x = (R[0, 1] + R[1, 0]) / s
            y = s / 4
            z = (R[1, 2] + R[2, 1]) / s
            w = (R[0, 2] - R[2, 0]) / s

        else:
            # z를 먼저 계산
            s = 2 * np.sqrt(
                1 - R[0, 0] - R[1, 1] + R[2, 2]
            )

            x = (R[0, 2] + R[2, 0]) / s
            y = (R[1, 2] + R[2, 1]) / s
            z = s / 4
            w = (R[1, 0] - R[0, 1]) / s

    # 어느 분기에서 계산했든 여기서 q에 저장
    q[0] = x
    q[1] = y
    q[2] = z
    q[3] = w

    # 단위 쿼터니언으로 정규화
    q = q / np.linalg.norm(q)

    # q와 -q는 같은 회전이므로 w >= 0 규약 사용
    if q[3] < 0:
        q = -q

    return q

def quaternion_to_matrix(q) -> np.ndarray:
    """단위 쿼터니언 (x, y, z, w) -> 회전행렬 (3,3).

        R = [[1 - 2(y^2 + z^2),   2(xy - zw),        2(xz + yw)],
             [2(xy + zw),         1 - 2(x^2 + z^2),  2(yz - xw)],
             [2(xz - yw),         2(yz + xw),        1 - 2(x^2 + y^2)]]

    입력이 정확히 단위가 아닐 수 있으므로 먼저 정규화한다. q 와 -q 는 같은 R 을 준다.
    """
    # TODO: 문제 3-1
    # 쿼터니언 정규화
    q = q / np.linalg.norm(q)

    # q와 -q는 같은 회전이므로 w >= 0으로 통일
    if q[3] < 0:
        q = -q

    x = q[0]
    y = q[1]
    z = q[2]
    w = q[3]

    R = np.array([
        [1 - 2 * (y*y + z*z),  2 * (x*y - z*w),      2 * (x*z + y*w)],
        [2 * (x*y + z*w),      1 - 2 * (x*x + z*z),  2 * (y*z - x*w)],
        [2 * (x*z - y*w),      2 * (y*z + x*w),      1 - 2 * (x*x + y*y)]
    ])

    return R
    

def quat_angle(q0, q1) -> float:
    """두 단위 쿼터니언이 나타내는 회전 사이의 각도 [rad], 0 <= angle <= pi.

        angle = 2 * arccos(|q0 . q1|)
    """
    # TODO: 문제 3-2 (slerp 안에서 재사용)
    return 2 * np.arccos(np.abs(np.dot(q0, q1)))


def slerp(q0, q1, t: float, eps: float = 1e-8) -> np.ndarray:
    """구면 선형 보간 (Spherical Linear intERPolation).

        d = q0 . q1                      (d < 0 이면 q1 = -q1, d = -d 로 짧은 호 선택)
        omega = arccos(d)
        q(t) = [sin((1-t) omega) q0 + sin(t omega) q1] / sin(omega)

    경계 상황
    - 두 자세가 거의 같아 d > 1 - eps 이면 sin(omega) ~ 0 이라 나눗셈이 불안정하다.
      이때는 선형 보간 후 정규화로 대체한다.
    - d 는 부동소수점 오차로 1 을 살짝 넘을 수 있으므로 clip 한다.

    반환값은 단위 쿼터니언이어야 한다. t = 0 이면 q0, t = 1 이면 (부호를 맞춘) q1.
    """
    # TODO: 문제 3-2 · 3-5
    q0 = np.asarray(q0, dtype=float)
    q1 = np.asarray(q1, dtype=float)

    # 1. 입력 쿼터니언을 단위 쿼터니언으로 정규화
    q0 = q0 / np.linalg.norm(q0)
    q1 = q1 / np.linalg.norm(q1)

    # 2. 두 쿼터니언의 내적
    d = np.dot(q0, q1)

    # 3. q와 -q는 같은 회전을 나타내므로
    #    짧은 호를 선택하기 위해 q1의 부호를 맞춘다.
    if d < 0:
        q1 = -q1
        d = -d

    # 부동소수점 오차 방지
    d = np.clip(d, -1.0, 1.0)

    # 4. 두 회전이 거의 같으면 SLERP 대신
    #    선형 보간(LERP) + 정규화
    if d > 1.0 - eps:
        q = (1.0 - t) * q0 + t * q1
        q = q / np.linalg.norm(q)
        return q

    # 5. 일반적인 SLERP
    omega = np.arccos(d)
    sin_omega = np.sin(omega)

    q = (
        np.sin((1.0 - t) * omega) * q0
        + np.sin(t * omega) * q1
    ) / sin_omega

    # 수치 오차를 조금 더 줄이기 위해 정규화
    q = q / np.linalg.norm(q)

    return q


def lerp_quat(q0, q1, t: float, normalize: bool = False) -> np.ndarray:
    """성분별 단순 선형 보간 (비교용).

        q(t) = (1 - t) q0 + t q1          (q0 . q1 < 0 이면 q1 부호를 먼저 뒤집는다)

    normalize=False 이면 정규화하지 않은 값을 그대로 돌려준다 — 크기가 1 에서 얼마나
    벗어나는지 관찰하는 데 쓴다. normalize=True 이면 정규화한다 (NLERP).
    """
    # TODO: 문제 3-4
    q0 = np.asarray(q0, dtype=float)
    q1 = np.asarray(q1, dtype=float)

    # 내적이 음수이면 긴 호(Long Arc)를 돌지 않도록 q1의 부호를 반전 (최단 경로)
    if np.dot(q0, q1) < 0.0:
        q1 = -q1

    # 성분별 선형 보간
    q = (1.0 - t) * q0 + t * q1

    if normalize:
        norm = np.linalg.norm(q)
        if norm > 1e-12:
            q = q / norm

    return q
