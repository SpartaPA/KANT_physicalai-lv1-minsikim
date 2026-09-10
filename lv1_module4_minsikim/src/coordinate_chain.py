"""문제 6 — 좌표 변환 체인 모듈. (학생 작성용 템플릿)

base -> link -> camera 로 이어지는 동차변환 체인을 구성하고,
카메라 기준 좌표를 로봇 base 기준으로 바꾼다.
모듈 4(픽앤플레이스 미니 프로젝트)에서 그대로 import 해 쓰게 되므로,
공개 함수 이름과 반환 형식을 이 템플릿 그대로 유지한다.
"""

from __future__ import annotations

import numpy as np

from .rotation import axis_angle_from_matrix, rot_x, rot_y, rot_z
from .transform import inv_T, make_T, transform_points

__all__ = ["CoordinateChain", "default_chain", "camera_point_to_base", "base_point_to_camera"]


class CoordinateChain:
    """부모 -> 자식 동차변환을 이름으로 등록하고, 임의의 두 프레임 사이 변환을 만든다.

    TF2 의 축소판이라고 보면 된다.

    Examples
    --------
    >>> chain = CoordinateChain("base")
    >>> chain.add("base", "link", T_base_link)
    >>> chain.add("link", "camera", T_link_camera)
    >>> T = chain.T("base", "camera")     # camera 좌표 -> base 좌표
    """

    def __init__(self, root: str = "base"):
        self.root = root
        self._parent: dict[str, str] = {}                 # child -> parent
        self._T: dict[tuple[str, str], np.ndarray] = {}   # (parent, child) -> T

    def add(self, parent: str, child: str, T) -> "CoordinateChain":
        """parent 기준으로 표현된 child 프레임의 자세 T(parent<-child) 를 등록한다.

        체이닝이 되도록 self 를 돌려준다. 4x4 가 아니면 ValueError.
        """
        T = np.asarray(T, dtype=float)
        if T.shape != (4, 4):
            raise ValueError(f"4x4 동차변환이 필요합니다. 받은 shape={T.shape}")
        self._parent[child] = parent
        self._T[(parent, child)] = T
        return self

    def get(self, parent: str, child: str) -> np.ndarray:
        """등록해 둔 T(parent <- child) 를 그대로 돌려준다."""
        return self._T[(parent, child)]

    def frames(self) -> list[str]:
        """등록된 프레임 이름 목록 (root 포함)."""
        return [self.root] + list(self._parent.keys())

    # ------------------------------------------------------ 여기부터 구현

    def _path_to_root(self, frame: str) -> list[str]:
        """frame 에서 root 까지의 경로 [frame, ..., root] 를 만든다.

        root 에 연결되어 있지 않으면 KeyError.
        """
        # TODO: 문제 6-1
        path = []
        current = frame

        while current != self.root:
            path.append(current)

            if current not in self._parent:
                raise KeyError(current)

            current = self._parent[current]

        path.append(self.root)

        return path
        
    def T_from_root(self, frame: str) -> np.ndarray:
        """root 기준 frame 의 자세 T(root <- frame).

        경로를 따라가며 등록된 변환을 곱한다. 곱하는 **순서**에 주의할 것:
        윗첨자/아랫첨자가 이웃끼리 상쇄되도록 놓으면 틀리지 않는다.
            T(base<-camera) = T(base<-link) @ T(link<-camera)
        """
        # TODO: 문제 6-1
        path = self._path_to_root(frame)
        T = np.eye(4)
        
        for child, parent in zip(path[:-1], path[1:]):
            T = self._T[parent, child] @ T
        
        return T
        
    def T(self, target: str, source: str) -> np.ndarray:
        """source 좌표를 target 좌표로 바꾸는 변환 T(target <- source).

        힌트: T(target<-source) = inv(T(root<-target)) @ T(root<-source)
        """
        # TODO: 문제 6-1
        target_T = self.T_from_root(target)
        source_T = self.T_from_root(source)
        return np.linalg.inv(target_T) @ source_T

    def transform(self, target: str, source: str, P, w: float = 1.0) -> np.ndarray:
        """source 프레임의 점(w=1) 또는 방향(w=0)을 target 프레임으로 변환한다.

        (3,) 와 (N,3) 을 모두 지원해야 하고, **반복문을 쓰지 않는다**.
        """
        # TODO: 문제 6-2
        # 1. source → target 변환행렬 가져오기
        T = self.T(target, source)

        # 2. P를 NumPy 배열로 만들기
        P = np.asarray(P)

        # 3. homogeneous coordinate 추가
        #    [x,y,z] → [x,y,z,w]
        if P.ndim == 1:
            P_h = np.append(P, w)
            # 마지막 w 성분 제거
            # [x,y,z,w] → [x,y,z]
            return (T @ P_h)[:3]
        else:
            P_h = np.hstack([
                P, np.full((P.shape[0], 1), w)
            ])
            
            return (P_h @ T.T)[:, :3]

    def axis_angle(self, target: str, source: str):
        """T(target <- source) 의 회전 부분에서 회전축과 회전각을 복원한다."""
        # TODO: 문제 6-4
        T = self.T(target, source)
        R = T[:3, :3]

        cos_theta = (np.trace(R) - 1.0) / 2.0
        cos_theta = np.clip(cos_theta, -1.0, 1.0)

        theta = np.arccos(cos_theta)

        # 회전각이 0에 가까운 경우
        if np.isclose(theta, 0.0):
            axis = np.array([1.0, 0.0, 0.0])

        # 회전각이 pi에 가까운 경우
        elif np.isclose(theta, np.pi):
            axis = np.sqrt((np.diag(R) + 1.0) / 2.0)

            # 부호를 결정
            if np.isclose(axis[0], 0.0):
                axis[1] = np.copysign(axis[1], R[0, 1])
            if np.isclose(axis[1], 0.0):
                axis[2] = np.copysign(axis[2], R[0, 2])
            if np.isclose(axis[2], 0.0):
                axis[2] = np.copysign(axis[2], R[1, 2])

            axis /= np.linalg.norm(axis)

        # 일반적인 경우
        else:
            axis = np.array([
                R[2, 1] - R[1, 2],
                R[0, 2] - R[2, 0],
                R[1, 0] - R[0, 1],
            ]) / (2.0 * np.sin(theta))

            axis /= np.linalg.norm(axis)

        return axis, theta


def default_chain() -> CoordinateChain:
    """과제에서 쓸 기본 체인(base -> link -> camera)을 만든다.

    지시문은 '임의의 회전·병진'을 쓰라고 하지만, 채점 수치를 맞추기 위해
    아래 값을 **그대로** 쓴다. (노트북 6-1 의 검증 셀이 이 값을 확인한다)

    base -> link   : z축 22.5도 회전 후 (0.35, 0.05, 0.45) m 이동
    link -> camera : `T_link_cam` = T(link ← camera) | y축 -20도 후 x축 90도 (`rot_y @ rot_x`) | (0.10, 0.05, 0.15) |
    T_cam_obj = T(camera ← object) | z축 25도 후 x축 -90도 (`rot_z @ rot_x`) | (0.05, -0.02, 0.60) — 카메라 앞 60 cm |
    """
    # TODO: 문제 6-1
    T_base_link   = make_T(rot_z(np.deg2rad(30)), [0.3,0.0,0.4])
    T_link_camera = make_T(rot_y(np.deg2rad(-20)) @ rot_x(np.deg2rad(90)), [0.1, 0.05, 0.15])
    
    return CoordinateChain("base") \
        .add("base", "link", T_base_link) \
        .add("link", "camera", T_link_camera) \
        # .add("camera", "object", T_camera_object)


def camera_point_to_base(p_cam, chain: CoordinateChain | None = None) -> np.ndarray:
    """카메라 기준 좌표 -> base 기준 좌표. (3,) 와 (N,3) 모두 지원.

    chain 이 None 이면 default_chain() 을 쓴다.
    """
    # TODO: 문제 6-1
    raise NotImplementedError("camera_point_to_base 를 구현하세요")


def base_point_to_camera(p_base, chain: CoordinateChain | None = None) -> np.ndarray:
    """base 기준 좌표 -> 카메라 기준 좌표. 왕복 검증(문제 6-2)에 쓴다."""
    # TODO: 문제 6-2
    raise NotImplementedError("base_point_to_camera 를 구현하세요")
