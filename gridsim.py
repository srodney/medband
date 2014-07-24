__author__ = 'rodney'
import mpltools
from matplotlib import cm
import numpy as np
from matplotlib import pyplot as pl

ALPHA2FILTER = {'H':'F160W','N':'F140W','J':'F125W',
                'Q':'F153M','P':'F139M','O':'F127M',
                '7':'F763M','8':'F845M',
                'X':'F775W','I':'F814W',
                }


def dosimGrid( sn, ngridz=50, bands='X7I8LYOJPNQH',
               x1range=[-2,2], crange=[-0.2,0.5],
               avrange=[0,0.7], trestrange = [-5,5],
               clobber=0, verbose=1 ) :
    """ set up and run a SNANA Grid simulation to show the
    medium band technique.
    """
    import stardust
    simname = 'sim_'+sn.nickname+'_medbandGrid'
    zrange = [ sn.z - sn.zerr, sn.z + sn.zerr ]

    stardust.simulate.mkgridsimlib( simname+'.simlib', survey='HST',
                                    field='default', bands=bands,
                                    clobber=clobber )

    stardust.simulate.mkinputGrid(
        simname+'_Ia', inputfile=simname+'_Ia.input', simlibfile=simname+'.simlib',
        simtype='Ia', clobber=clobber,
        GENFILTERS=bands,
        NGRID_TREST=10,    GENRANGE_TREST=trestrange,
        NGRID_LOGZ=ngridz,     GENRANGE_REDSHIFT=zrange,
        NGRID_LUMIPAR=10,  GENRANGE_SALT2X1=x1range,
        NGRID_COLORPAR=10, GENRANGE_SALT2C=crange,
        NGRID_COLORLAW=1,  GENRANGE_RV=[3.1,3.1] )

    # stardust.simulate.mkinput( simname+'_Ibc', inputfile=simname+'_Ibc.input',
    #                                simlibfile=simname+'.simlib',
    #                                simtype='Ibc', ratemodel='flat',
    #                                clobber=clobber, GENSOURCE='GRID',
    #                                GENFILTERS=bands,
    #                                GENPERFECT=2, GENRANGE_REDSHIFT=zrange,
    #                                 smear=False,
    #                                GENRANGE_AV=avrange, )

    # stardust.simulate.mkinput( simname+'_II', inputfile=simname+'_II.input',
    #                            simlibfile=simname+'.simlib',
    #                            simtype='II', rate='flat',
    #                            clobber=clobber,
    #                            GENFILTERS=bands, GENSOURCE='GRID',
    #                            GENPERFECT=2, GENRANGE_REDSHIFT=zrange,
    #                            smear=False,
    #                            GENRANGE_AV=avrange, )

    stardust.simulate.dosim('%s_Ia.input'%simname, verbose=verbose )
    # stardust.simulate.dosim('%s_Ibc.input'%simname, perfect=True, verbose=verbose )
    # stardust.simulate.dosim('%s_II.input'%simname, perfect=True, verbose=verbose )

    simdat = stardust.SimTable( '%s_Ia'%simname)
    return( simdat )



def plotgridz( simgridIa, medbands='OPQ', broadbands='JNH' ):
    """  Plot medium-broad pseudo-colors from a grid simulation as a function
     of redshift.

    :param simgridIa: SNANA Simulation Table, or None to make/load it anew
    :param clobber:  passed to gridsim.dosimGrid() to re-run the SNANA sims
    :return: nothing
    """
    cmap = cm.jet
    z = simgridIa.z

    nrows = len(broadbands)
    for medband, broadband, irow in zip(medbands,broadbands,range(nrows)) :
        medfilt = ALPHA2FILTER[medband]
        broadfilt = ALPHA2FILTER[broadband]
        iB = simgridIa.BANDS.index( broadband )
        iM = simgridIa.BANDS.index( medband )

        irv=0

        ax1 = pl.subplot(nrows,3,1+irow*3)
        ax2 = pl.subplot(nrows,3,2+irow*3,sharex=ax1, sharey=ax1)
        ax3 = pl.subplot(nrows,3,3+irow*3,sharex=ax1, sharey=ax1)

        mpltools.color.cycle_cmap( len(simgridIa.LUMIPAR),  cmap=cmap, ax=ax1)
        mpltools.color.cycle_cmap( len(simgridIa.COLORPAR), cmap=cmap, ax=ax2)

        iage = np.argmin(np.abs(simgridIa.TREST-0))
        ic = np.argmin(np.abs(simgridIa.COLORPAR-0))
        for x1 in simgridIa.LUMIPAR :
            ix1 = np.argmin(np.abs(simgridIa.LUMIPAR-x1))

            B = simgridIa.LCMATRIX[ ix1, irv, ic, :, iB, iage ]
            M = simgridIa.LCMATRIX[ ix1, irv, ic, :, iM, iage ]
            ax1.plot( z, M-B,  marker='o', ls=' ' )

        ix1 = np.argmin(np.abs(simgridIa.LUMIPAR-0))
        iage = np.argmin(np.abs(simgridIa.TREST-0))
        for c in simgridIa.COLORPAR :
            ic = np.argmin(np.abs(simgridIa.COLORPAR-c))
            B = simgridIa.LCMATRIX[ ix1, irv, ic, :, iB, iage ]
            M = simgridIa.LCMATRIX[ ix1, irv, ic, :, iM, iage ]
            ax2.plot( z, M-B, marker='o', ls=' ' )

        ix1 = np.argmin(np.abs(simgridIa.LUMIPAR-0))
        ic = np.argmin(np.abs(simgridIa.COLORPAR-0))
        for age in simgridIa.TREST :
            iage = np.argmin(np.abs(simgridIa.TREST-age))
            B = simgridIa.LCMATRIX[ ix1, irv, ic, :, iB, iage ]
            M = simgridIa.LCMATRIX[ ix1, irv, ic, :, iM, iage ]
            ax3.plot( z, M-B, marker='o', ls=' ' )

        # TODO : use http://tonysyu.github.io/mpltools/auto_examples/color/plot_color_mapper.html

        if irow==0 :
            ax1.text( 0.15, 0.05, 'x1 : %.1f'%simgridIa.LUMIPAR[0], color=cmap(0.0) , transform=ax1.transAxes)
            ax1.text( 0.4, 0.05, '.. %.1f'%simgridIa.LUMIPAR[-1], color=cmap(1.0) , transform=ax1.transAxes)
            ax1.text( 0.05, 0.95, 'c=0,age=0', color='k', transform=ax1.transAxes, ha='left',va='top')
            ax2.text( 0.15, 0.05, 'c : %.1f' %simgridIa.COLORPAR[0], color=cmap(0.0), transform=ax2.transAxes )
            ax2.text( 0.4, 0.05, '.. %.1f'%simgridIa.COLORPAR[-1], color=cmap(1.0), transform=ax2.transAxes )
            ax2.text( 0.05, 0.95, 'x1=0,age=0', color='k', transform=ax2.transAxes, ha='left',va='top')
            ax3.text( 0.15, 0.05, 'age : %.1f'%simgridIa.TREST[0], color=cmap(0.0), transform=ax3.transAxes )
            ax3.text( 0.4, 0.05, '.. %.1f'% simgridIa.TREST[-1], color=cmap(1.0), transform=ax3.transAxes )
            ax3.text( 0.05, 0.95, 'x1=0,c=0', color='k', transform=ax3.transAxes, ha='left',va='top')
        if irow == nrows-1 :
            ax1.set_xlabel('redshift')
            ax2.set_xlabel('redshift')
            ax3.set_xlabel('redshift')
        ax1.set_ylabel('%s-%s'%(medfilt, broadfilt) )
        pl.setp( ax2.yaxis.get_ticklabels(), visible=False )
    return

def plotgridCircle( simgridIa, color1, color2, x1=0, c=0, age=0 ):
    """ Plot a SNANA grid simulation into a color-color circle diagram.
    :param simdatGrid:
    :param color1:
    :param color2:
    :return:
    """

    medband1,broadband1 = color1.split('-')
    # medfilt1 = ALPHA2FILTER[medband1]
    # broadfilt1 = ALPHA2FILTER[broadband1]
    iB1 = simgridIa.BANDS.index( broadband1 )
    iM1 = simgridIa.BANDS.index( medband1 )

    medband2,broadband2 = color2.split('-')
    # medfilt2 = ALPHA2FILTER[medband2]
    # broadfilt2 = ALPHA2FILTER[broadband2]
    iB2 = simgridIa.BANDS.index( broadband2 )
    iM2 = simgridIa.BANDS.index( medband2 )

    irv=0
    cmap = cm.jet
    z = simgridIa.z

    iage = np.argmin(np.abs(simgridIa.TREST-age))
    ic = np.argmin(np.abs(simgridIa.COLORPAR-c))
    ix1 = np.argmin(np.abs(simgridIa.LUMIPAR-x1))
    B1 = simgridIa.LCMATRIX[ ix1, irv, ic, :, iB1, iage ]
    M1 = simgridIa.LCMATRIX[ ix1, irv, ic, :, iM1, iage ]

    B2 = simgridIa.LCMATRIX[ ix1, irv, ic, :, iB2, iage ]
    M2 = simgridIa.LCMATRIX[ ix1, irv, ic, :, iM2, iage ]

    mpltools.color.cycle_cmap( len(z),  cmap=cmap )
    for iz in range(len(z)) :
        pl.plot( M1[iz:iz+2]-B1[iz:iz+2], M2[iz:iz+2]-B2[iz:iz+2], marker=' ', ls='-', lw=2 )
