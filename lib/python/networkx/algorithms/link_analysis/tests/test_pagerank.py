#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
import networkx

# Example from
# A. Langville and C. Meyer, "A survey of eigenvector methods of web
# information retrieval."  http://citeseer.ist.psu.edu/713792.html


class TestPageRank:

    def setUp(self):
        
        G=networkx.DiGraph()
        edges=[(1,2),(1,3),\
           (3,1),(3,2),(3,5),\
           (4,5),(4,6),\
           (5,4),(5,6),\
           (6,4)]
           
        G.add_edges_from(edges)
        self.G=G
        self.G.pagerank=dict(zip(G,
                                 [0.03721197,0.05395735,0.04150565,
                                  0.37508082,0.20599833, 0.28624589]))

    def test_pagerank(self):
        G=self.G
        p=networkx.pagerank(G,alpha=0.9,tol=1.e-08)
        for n in G:
            assert_almost_equal(p[n],G.pagerank[n],places=4)

    def test_numpy_pagerank(self):
        try:
            import numpy
        except ImportError:
            raise SkipTest('numpy not available.')
        G=self.G
        p=networkx.pagerank_numpy(G,alpha=0.9)
        for n in G:
            assert_almost_equal(p[n],G.pagerank[n],places=4)    


    def test_google_matrix(self):
        try:
            import numpy.linalg
        except ImportError:
            raise SkipTest('numpy not available.')
        G=self.G
        M=networkx.google_matrix(G,alpha=0.9)
        e,ev=numpy.linalg.eig(M.T)
        p=numpy.array(ev[:,0]/ev[:,0].sum())[:,0]
        for (a,b) in zip(p,self.G.pagerank.values()):
            assert_almost_equal(a,b)


    def test_scipy_pagerank(self):
        G=self.G
        try:
            import scipy
        except ImportError:
            raise SkipTest('scipy not available.')
        p=networkx.pagerank_scipy(G,alpha=0.9,tol=1.e-08)
        for n in G:
            assert_almost_equal(p[n],G.pagerank[n],places=4)    





