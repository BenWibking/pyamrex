# -*- coding: utf-8 -*-

import pytest
import numpy as np
import amrex
from amrex import Geometry as Gm

# TODO: return coord?

@pytest.fixture
def box():
    return amrex.Box(amrex.IntVect(0,0,0), amrex.IntVect(127,127,127))

@pytest.fixture
def real_box():
    return amrex.RealBox([0,0,0],[1,2,5])

@pytest.fixture
def geometry(box, real_box):
    coord = 1
    is_periodic = [0,0,1]
    return amrex.Geometry(box, real_box, coord, is_periodic)

@pytest.mark.skipif(amrex.Config.spacedim != 3,
                    reason="Requires AMREX_SPACEDIM = 3")
def test_geometry_define(box,real_box):
    gm = Gm()
    coord = 1
    is_periodic = [0,0,1]
    gm.define(box, real_box, coord, is_periodic)
    assert(gm.ProbLength(0) == 1 and
            gm.ProbLength(1) == 2 and
            gm.ProbLength(2) == 5)
    assert(gm.isPeriodic() == is_periodic)

@pytest.mark.skipif(amrex.Config.spacedim != 3,
                    reason="Requires AMREX_SPACEDIM = 3")
def test_probDomain(box,real_box):
    gm = Gm()
    coord = 1
    is_periodic = [0,0,1]
    gm.define(box, real_box, coord, is_periodic)
    assert(gm.ok())

    lo = [0,-1,1]
    hi = [1,0,2]
    rb = amrex.RealBox(lo,hi)
    gm.ProbDomain(rb)
    assert(np.isclose(gm.ProbLo(0), lo[0]) and
            np.isclose(gm.ProbLo(1), lo[1]) and
            np.isclose(gm.ProbLo(2), lo[2]) and
            np.isclose(gm.ProbHi(0), hi[0]) and
            np.isclose(gm.ProbHi(1), hi[1]) and
            np.isclose(gm.ProbHi(2), hi[2]))


@pytest.mark.skipif(amrex.Config.spacedim != 3,
                    reason="Requires AMREX_SPACEDIM = 3")
def test_size(geometry):
    gm = geometry

    assert(np.isclose(gm.ProbSize(), 10))
    assert(np.isclose(gm.ProbLength(0), 1))
    assert(np.isclose(gm.ProbLength(1), 2))
    assert(np.isclose(gm.ProbLength(2), 5))

@pytest.mark.skipif(amrex.Config.spacedim != 3,
                    reason="Requires AMREX_SPACEDIM = 3")
def test_domain(box,real_box):
    bx = amrex.Box(amrex.IntVect(0, 0, 0), amrex.IntVect(127, 127, 127))
    gm = Gm()
    coord = 1
    is_periodic = [0,0,1]
    gm.define(box, real_box, coord, is_periodic)
    assert(gm.ok())

    gm.Domain(bx)    
    assert(gm.Domain().small_end == bx.small_end and 
           gm.Domain().big_end == bx.big_end)

@pytest.mark.skipif(amrex.Config.spacedim != 3,
                    reason="Requires AMREX_SPACEDIM = 3")
def test_periodic_queries(box, real_box):
    coord = 1
    is_periodic = [0,0,1]
    gm = Gm(box, real_box, coord, is_periodic)

    pdcity = gm.periodicity()

    assert(gm.isAnyPeriodic())
    assert(not gm.isPeriodic(0) and not gm.isPeriodic(1) and gm.isPeriodic(2))
    assert(not gm.isAllPeriodic())
    assert(gm.isPeriodic() == is_periodic)
    gm.setPeriodicity([0,0,0])
    assert(not gm.isAnyPeriodic())
    gm.setPeriodicity([1,1,1])
    assert(gm.isAllPeriodic())

@pytest.mark.skipif(amrex.Config.spacedim != 3,
                    reason="Requires AMREX_SPACEDIM = 3")
def test_periodicity(geometry):
    gm = geometry
    bx = gm.Domain()

    for non_periodic_coord in [0,1]:
        error_thrown = False
        try:
            gm.period(0)
        except RuntimeError:
            error_thrown = True
        assert(error_thrown)
    
    assert(gm.period(2) == bx.length(2))
    pdcity = amrex.Periodicity(bx.length() * amrex.IntVect(gm.isPeriodic()))
    assert(gm.periodicity() == pdcity)

    iv1 = amrex.IntVect(0,0,0)
    iv2 = amrex.IntVect(9,19,29)
    pdcity = amrex.Periodicity(amrex.IntVect(0,0,30))
    bx = amrex.Box(iv1,iv2)
    assert(gm.periodicity(bx) == pdcity)

@pytest.mark.skipif(amrex.Config.spacedim != 3,
                    reason="Requires AMREX_SPACEDIM = 3")
def test_grow(geometry):
    gm = geometry
    gm_grow_pd = gm.growPeriodicDomain(2)
    assert(gm_grow_pd.small_end == amrex.IntVect(0,0,-2))
    assert(gm_grow_pd.big_end == amrex.IntVect(127,127,129))
    gm_grow_npd = gm.growNonPeriodicDomain(3)
    assert(gm_grow_npd.small_end == amrex.IntVect(-3,-3,0))
    assert(gm_grow_npd.big_end == amrex.IntVect(130,130,127))
    

@pytest.mark.skipif(amrex.Config.spacedim != 3,
                    reason="Requires AMREX_SPACEDIM = 3")
def test_coarsen_refine(geometry):
    iv1 = amrex.IntVect(-1,-2,-3)
    iv2 = amrex.IntVect(4,5,6)
    bx = amrex.Box(iv1,iv2)
    rb = amrex.RealBox(-1,-2,-3,2,4,6)
    gmc = amrex.Geometry(bx,rb,1,[0,0,1])
    cv = amrex.IntVect(2,2,1)
    gmc.coarsen(cv)
    assert(gmc.Domain().small_end == amrex.IntVect(-1,-1,-3))
    assert(gmc.Domain().big_end == amrex.IntVect(2,2,6))

    gmr = amrex.Geometry(bx,rb,1,[0,0,1])
    rv = amrex.IntVect(2,2,3)
    gmr.refine(rv)
    assert(gmr.Domain().small_end == amrex.IntVect(-2,-4,-9))
    assert(gmr.Domain().big_end == amrex.IntVect(9,11,20))

@pytest.mark.skipif(amrex.Config.spacedim != 3,
                    reason="Requires AMREX_SPACEDIM = 3")
def test_roundoff_domain():
    iv1 = amrex.IntVect(-1,-2,-3)
    iv2 = amrex.IntVect(4,5,6)
    bx = amrex.Box(iv1,iv2)
    rb = amrex.RealBox(0,1.0002,0.00105,2,4.2,5)

    gm = Gm(bx,rb, 1, [0,0,1])

    assert(gm.outsideRoundOffDomain(-1.0,1,2))
    assert(not gm.outsideRoundOffDomain(1.00,2.,2))
    assert(not gm.insideRoundOffDomain(-1.0,1,2))
    assert(gm.insideRoundOffDomain(1.00,2.,2))


@pytest.mark.skipif(amrex.Config.spacedim != 3,
                    reason="Requires AMREX_SPACEDIM = 3")
def test_Resets():
    rb = amrex.RealBox(0,0,0,1,2,6)
    amrex.Geometry.ResetDefaultProbDomain(rb)
    Gm.ResetDefaultProbDomain(rb)
    is_periodic = [1,0,1]
    Gm.ResetDefaultPeriodicity(is_periodic)
    Gm.ResetDefaultCoord(1)
    
    gm = Gm()
    assert(np.isclose(gm.ProbLength(0), 1) and
            np.isclose(gm.ProbLength(1), 2) and
            np.isclose(gm.ProbLength(2), 6))
    assert(gm.isPeriodic() == is_periodic)
    print(gm.Coord())
    CType = amrex.CoordSys.CoordType
    assert(gm.Coord() == CType.RZ)