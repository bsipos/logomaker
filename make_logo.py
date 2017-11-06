from __future__ import division
import numpy as np
import inspect
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib as mpl
from validate import validate_parameter, validate_mat
from data import load_alignment, iupac_to_probability_mat, \
    counts_mat_to_probability_mat
from Logo import Logo
import data
import color
from load_meme import load_meme
from documentation_parser import document_function

import pdb

default_fig_width = 8
default_fig_height_per_line = 2

def remove_none_from_dict(d):
    """ Removes None values from a dictionary """
    assert isinstance(d, dict), 'Error: d is not a dictionary.'
    return dict([(k, v) for k, v in d.items() if v is not None])

def make_logo(matrix=None,

              # FASTA file processing
              fasta_file=None,

              # MEME file processing
              meme_file=None,
              meme_motifname=None,
              meme_motifnum=None,

              # IUPAC processing
              iupac_string=None,

              # CSV file processing
              csv_file=None,
              seq_col=None,
              ct_col=None,
              csv_kwargs={},
              background_csvfile=None,
              background_seqcol=None,
              background_ctcol=None,
              background_csvkwargs=None,

              # Matrix transformation (make_logo only)
              matrix_type=None,
              logo_type=None,
              background=None,
              pseudocount=1.0,
              enrichment_logbase=2,
              enrichment_centering=True,
              information_units='bits',
              counts_threshold=0,

              # Immediate drawing (make_logo only)
              figsize=None,
              draw_now=True,
              save_to_file=None,
              dpi=300,
              max_positions_per_line=50,

              # Position choice
              position_range=None,
              shift_first_position_to=None,

              # Character choice
              sequence_type=None,
              characters=None,
              ignore_characters='.-',

              # Character formatting
              colors='dodgerblue',
              alpha=1,
              edgecolors='black',
              edgealpha=1,
              edgewidth=0,
              boxcolors='white',
              boxedgecolors='black',
              boxedgewidth=0,
              boxalpha=0,
              boxedgealpha=0,

              # Highlighted character formatting
              highlight_sequence=None,
              highlight_colors=None,
              highlight_alpha=None,
              highlight_edgecolors=None,
              highlight_edgewidth=None,
              highlight_edgealpha=None,
              highlight_boxcolors=None,
              highlight_boxalpha=None,
              highlight_boxedgecolors=None,
              highlight_boxedgewidth=None,
              highlight_boxedgealpha=None,

              # Fixed character formatting
              fixedchar_dict={},
              fixedchar_colors='silver',
              fixedchar_alpha=1,
              fixedchar_edgecolors='black',
              fixedchar_edgewidth=0,
              fixedchar_edgealpha=1,
              fixedchar_boxcolors='white',
              fixedchar_boxalpha=0,
              fixedchar_boxedgecolors='black',
              fixedchar_boxedgewidth=0,
              fixedchar_boxedgealpha=1,

              # Character font
              font_properties=None,
              font_file=None,
              font_family=('Arial Rounded MT Bold', 'Arial', 'sans'),
              font_weight='bold',
              font_style=None,

              # Character placement
              stack_order='big_on_top',
              use_transparency=False,
              max_alpha_val=None,
              below_shade=1.,
              below_alpha=1.,
              below_flip=True,
              hpad=0.,
              vpad=0.,
              width=1.,
              vsep=0.,
              uniform_stretch=False,
              max_stretched_character=None,

              # Special axes formatting
              axes_type='classic',
              style_sheet=None,
              rcparams={},

              # Grid line formatting
              show_gridlines=None,
              gridline_axis=None,
              gridline_width=None,
              gridline_color=None,
              gridline_alpha=None,
              gridline_style=None,

              # Baseline formatting
              show_baseline=None,
              baseline_width=None,
              baseline_color=None,
              baseline_alpha=None,
              baseline_style=None,

              # vlines formatting
              vline_positions=(),
              vline_width=None,
              vline_color=None,
              vline_alpha=None,
              vline_style=None,

              # x-axis formatting
              xlim=None,
              xticks=None,
              xtick_spacing=None,
              xtick_anchor=0,
              xticklabels=None,
              xtick_rotation=None,
              xtick_length=None,
              xtick_format=None,
              xlabel=None,

              # y-axis formatting
              show_binary_yaxis=None,
              ylim=None,
              yticks=None,
              yticklabels=None,
              ytick_rotation=None,
              ytick_length=None,
              ytick_format=None,
              ylabel=None,

              # Other axis formatting
              title=None,
              left_spine=None,
              right_spine=None,
              top_spine=None,
              bottom_spine=None,
              use_tightlayout=True,

              # Default axes font
              axes_fontfile=None,
              axes_fontfamily='sans',
              axes_fontweight=None,
              axes_fontstyle=None,
              axes_fontsize=10,

              # tick font
              tick_fontfile=None,
              tick_fontfamily=None,
              tick_fontweight=None,
              tick_fontstyle=None,
              tick_fontsize=None,

              # label font
              label_fontfile=None,
              label_fontfamily=None,
              label_fontweight=None,
              label_fontstyle=None,
              label_fontsize=None,

              # title font
              title_fontfile=None,
              title_fontfamily=None,
              title_fontweight=None,
              title_fontstyle=None,
              title_fontsize=None,
              ):
    """
    Description:

        Generate a logo based on user-specified parameters

    Returns:

        If a single-line logo is drawn:
            logo (a logomaker.Logo object). The figure and axes on which the
                logo is drawn are saved in logo.fig and logo.ax respectively.
        If a multi-line logo is drawn:
            list of logomaker.Logo objects, one for each line.

    Arguments:
    """

    ######################################################################
    # Validate all parameters

    names, vargs, kwargs, default_values = inspect.getargspec(make_logo)
    user_values = [eval(name) for name in names]

    assert len(names)==len(default_values), \
        'len(names)==%d does not match len(default_values)==%d' %\
        (len(names), len(default_values))

    for name, user_value, default_value in \
            zip(names, user_values, default_values):

        # Validate parameter value
        valid_value = validate_parameter(name, user_value, default_value)

        # Set parameter value equal to the valid value
        exec("%s = valid_value" % name)

    ######################################################################
    # matrix

    # Initialize background matrix to none
    bg_mat = None

    # Make sure that only one of the following is specified
    exclusive_list = ['matrix',
                      'fasta_file',
                      'meme_file',
                      'iupac_string',
                      'csv_file']
    num_input_sources = sum([eval(x) is not None for x in exclusive_list])
    if num_input_sources != 1:
        assert False, \
            'Error: exactly one of the following must be specified: %s.' %\
            repr(exclusive_list)

    # If matrix is specified
    if matrix is not None:
        matrix = validate_mat(matrix)

    # Otherwise, if FASTA file is specifieid
    elif fasta_file is not None:
        matrix = load_alignment(fasta_file=fasta_file)
        matrix_type = 'counts'

    # Otherwise, if MEME file is specified
    elif meme_file is not None:
        matrix = load_meme(file_name=meme_file,
                           motif_name=meme_motifname,
                           motif_num=meme_motifnum)
        matrix_type = 'probability'

        # Set background based on MEME file if background is currently None
        meme_background = load_meme(file_name=meme_file, get_background=True)
        if background is None and meme_background is not None:
            background = meme_background

        # Set title to be matrix name if none is specified
        if title is None:
            title = matrix.name

    # Otherwise, if iupac_string is specified
    elif iupac_string is not None:
        matrix = iupac_to_probability_mat(iupac_string)
        matrix_type = 'probability'

        # Set title to be matrix name if none is specified
        if title is None:
            title = iupac_string

    # Otherwise, if csv file is specified
    elif csv_file is not None:
        matrix = load_alignment(csv_file=csv_file,
                                seq_col=seq_col,
                                ct_col=ct_col,
                                csv_kwargs=csv_kwargs)
        matrix_type = 'counts'

        # If either a background counts column or a
        # background csv file is specified
        if (background_ctcol is not None) or (background_csvfile is not None):

            # Set background csv parameters, defaulting to foreground
            # CSV parameters
            if background_csvfile is None:
                background_csvfile = csv_file
            if background_seqcol is None:
                background_seqcol = seq_col
            if background_ctcol is None:
                background_ctcol = ct_col
            if background_csvkwargs is None:
                background_csvkwargs = csv_kwargs

            # Load background counts from csv file
            bg_countsmat = load_alignment(csv_file=background_csvfile,
                                          seq_col=background_seqcol,
                                          ct_col=background_ctcol,
                                          csv_kwargs=background_csvkwargs)

            # Transform background counts matrix to a probability matrix
            bg_mat = counts_mat_to_probability_mat(count_mat=bg_countsmat,
                                                   pseudocount=pseudocount)

    else:
        assert False, 'This should never happen.'

    ######################################################################
    # matrix.columns

    # Filter matrix columns based on sequence and character specifications
    matrix = data.filter_columns(matrix=matrix,
                                 sequence_type=sequence_type,
                                 characters=characters,
                                 ignore_characters=ignore_characters)
    characters = matrix.columns

    ######################################################################
    # matrix.index

    # If matrix_type is counts, remove positions with too few counts
    if matrix_type == 'counts':
        position_counts = matrix.values.sum(axis=1)
        matrix = matrix.loc[position_counts >= counts_threshold, :]

    # Restrict to specific position range if requested
    if position_range is not None:
        min = position_range[0]
        max = position_range[1]
        indices = (matrix.index >= min) & (matrix.index < max)
        matrix = matrix.loc[indices, :]

        # Process bg_mat if that has been set
        if bg_mat is not None:
            bg_mat = bg_mat.loc[indices, :]

    # Matrix length is now set. Record it.
    L = len(matrix)

    # Shift positions to requested start if so requested
    if shift_first_position_to is None:
        matrix['pos'] = matrix.index
    else:
        matrix['pos'] = shift_first_position_to + matrix.index \
                        - matrix.index[0]

    # Enforce integer positions and set as index
    matrix['pos'] = matrix['pos'].astype(int)
    matrix.set_index('pos', inplace=True, drop=True)
    matrix = validate_mat(matrix)
    positions = matrix.index

    ######################################################################
    # matrix.values

    # Set logo_type equal to matrix_type if is currently None
    if logo_type is None:
        logo_type = matrix_type
    logo_type = validate_parameter('logo_type', logo_type, None)

    # Get background matrix, only if it has not yet been set
    if bg_mat is None:
        bg_mat = data.set_bg_mat(background, matrix)

    # Transform matrix:
    matrix = data.transform_mat(matrix=matrix,
                                from_type=matrix_type,
                                to_type=logo_type,
                                pseudocount=pseudocount,
                                background=bg_mat,
                                enrichment_logbase=enrichment_logbase,
                                enrichment_centering=enrichment_centering,
                                information_units=information_units)

    ######################################################################
    # multi-line logos
    if L > max_positions_per_line:

        # Compute the number of lines needed
        num_lines = int(np.ceil(L / max_positions_per_line))

        # Set figsize
        fig_height = num_lines * default_fig_height_per_line
        if figsize is None:
            figsize = [default_fig_width, fig_height]

        # Pad matrix with zeros
        rows = matrix.index[0] + \
               np.arange(L, num_lines * max_positions_per_line)
        for r in rows:
            matrix.loc[r, :] = 0.0

        # If there is a background matrix, pad it with ones:
        if bg_mat is not None:
            for r in rows:
                bg_mat.loc[r, :] = 1./bg_mat.shape[1]

        # If there is a highlight sequence, pad it too
        if highlight_sequence is not None:
            highlight_sequence = highlight_sequence + \
                                 ' '*(num_lines * max_positions_per_line - L)

        # Get arguments passed by user
        kwargs = dict(zip(names, user_values))

        # Set ylim (will not be None)
        if ylim is None:
            ymax = (matrix.values * (matrix.values > 0)).sum(axis=1).max()
            ymin = (matrix.values * (matrix.values < 0)).sum(axis=1).min()
            ylim = [ymin, ymax]

        # Set style sheet:
        if style_sheet is not None:
            if style_sheet == 'default':
                mpl.rcdefaults()
            else:
                plt.style.use(style_sheet)

        # Create figure
        if draw_now:
            fig, axs = plt.subplots(num_lines, 1, figsize=figsize)

        logos = []
        for n in range(num_lines):

            # Section matrix
            start = int(n * max_positions_per_line)
            stop = int((n+1) * max_positions_per_line)
            n_matrix = matrix.iloc[start:stop, :]

            # If there is a background matrix, section it
            if bg_mat is not None:
                n_bgmat = bg_mat.iloc[start:stop, :]

            # If there is a highlight sequence, section it
            if highlight_sequence is not None:
                n_highlight_sequence = highlight_sequence[start:stop]
            else:
                n_highlight_sequence = None

            # Adjust kwargs
            n_kwargs = kwargs.copy()

            # Use only matrix and background as input, not files or iupac
            # To do this, first set all input variables to None
            for var_name in exclusive_list:
                n_kwargs[var_name] = None

            # Then pass sectioned matrices to matrics and background.
            n_kwargs['matrix'] = n_matrix
            n_kwargs['background'] = n_bgmat

            # Preserve matrix and logo type
            n_kwargs['matrix_type'] = logo_type
            n_kwargs['logo_type'] = logo_type

            # Pass sectioned highlight_sequence
            n_kwargs['highlight_sequence'] = n_highlight_sequence

            # Pass shifted shift_first_position_to
            n_kwargs['shift_first_position_to'] = matrix.index[0] + start

            # Don't draw each individual logo. Wait until all are returned.
            n_kwargs['figsize'] = None
            n_kwargs['draw_now'] = False
            n_kwargs['ylim'] = ylim

            # Adjust annotation
            if n != 0:
                n_kwargs['title'] = ''
            if n != num_lines-1:
                n_kwargs['xlabel'] = ''

            # Create logo
            logo = make_logo(**n_kwargs)
            if draw_now:
                logo.fig = fig
                logo.ax = axs[n]
                logo.draw(logo.ax)
            else:
                logo.fig = None
                logo.ax = None
            logos.append(logo)

        return logos

    ######################################################################
    # font_properties

    # If font_properties is set directly by user, validate it
    if font_properties is not None:
        assert isinstance(font_properties, FontProperties), \
            'Error: font_properties is not an instance of FontProperties.'
    # Otherwise, create font_properties from other font information
    else:

        # Create properties
        font_properties = FontProperties(family=font_family,
                                         weight=font_weight,
                                         fname=font_file,
                                         style=font_style)

    ######################################################################
    # character_style

    character_style = {
        'facecolors': color.get_color_dict(color_scheme=colors,
                                           chars=characters,
                                           alpha=alpha),
        'edgecolors': color.get_color_dict(color_scheme=edgecolors,
                                           chars=characters,
                                           alpha=edgealpha),
        'boxcolors': color.get_color_dict(color_scheme=boxcolors,
                                          chars=characters,
                                          alpha=boxalpha),
        'boxedgecolors': color.get_color_dict(color_scheme=boxedgecolors,
                                              chars=characters,
                                              alpha=boxedgealpha),
        'edgewidth': edgewidth,
        'boxedgewidth': boxedgewidth,
    }

    ######################################################################
    # highlight_style

    # Set higlighted character format
    highlight_colors = highlight_colors \
        if highlight_colors is not None \
        else colors
    highlight_alpha = float(highlight_alpha) \
        if highlight_alpha is not None \
        else alpha
    highlight_edgecolors = highlight_edgecolors \
        if highlight_edgecolors is not None \
        else edgecolors
    highlight_edgewidth = highlight_edgewidth \
        if highlight_edgewidth is not None \
        else edgewidth
    highlight_edgealpha = float(highlight_edgealpha) \
        if highlight_edgealpha is not None \
        else edgealpha
    highlight_boxcolors = highlight_boxcolors \
        if highlight_boxcolors is not None \
        else boxcolors
    highlight_boxalpha = float(highlight_boxalpha) \
        if highlight_boxalpha is not None \
        else boxalpha
    highlight_boxedgecolors = highlight_boxedgecolors \
        if highlight_boxedgecolors is not None \
        else boxedgecolors
    highlight_boxedgewidth = highlight_boxedgewidth \
        if highlight_boxedgewidth is not None \
        else boxedgewidth
    highlight_boxedgealpha = highlight_boxedgealpha \
        if highlight_boxedgealpha is not None \
        else boxedgealpha

    highlight_style = {
        'facecolors': color.get_color_dict(color_scheme=highlight_colors,
                                           chars=characters,
                                           alpha=highlight_alpha),
        'edgecolors': color.get_color_dict(color_scheme=highlight_edgecolors,
                                           chars=characters,
                                           alpha=highlight_edgealpha),
        'boxcolors': color.get_color_dict(color_scheme=highlight_boxcolors,
                                          chars=characters,
                                          alpha=highlight_boxalpha),
        'boxedgecolors': color.get_color_dict(
                                          color_scheme=highlight_boxedgecolors,
                                          chars=characters,
                                          alpha=highlight_boxedgealpha),
        'edgewidth': highlight_edgewidth,
        'boxedgewidth': highlight_boxedgewidth,
    }

    ######################################################################
    # fixedchar_style

    fixed_characters = set(fixedchar_dict.values())
    fixedchar_style = {
        'facecolors': color.get_color_dict(color_scheme=fixedchar_colors,
                                           chars=fixed_characters,
                                           alpha=fixedchar_alpha),
        'edgecolors': color.get_color_dict(color_scheme=fixedchar_edgecolors,
                                           chars=fixed_characters,
                                           alpha=fixedchar_edgealpha),
        'boxcolors': color.get_color_dict(color_scheme=fixedchar_boxcolors,
                                          chars=fixed_characters,
                                          alpha=fixedchar_boxalpha),
        'boxedgecolors': color.get_color_dict(
                                          color_scheme=fixedchar_boxedgecolors,
                                          chars=fixed_characters,
                                          alpha=fixedchar_boxedgealpha),
        'edgewidth': fixedchar_edgewidth,
        'boxedgewidth': fixedchar_boxedgewidth,
    }

    ######################################################################
    # placement_style

    placement_style = {
        'stack_order': stack_order,
        'use_transparency': use_transparency,
        'max_alpha_val': max_alpha_val,
        'below_shade': below_shade,
        'below_alpha': below_alpha,
        'below_flip': below_flip,
        'hpad': hpad,
        'vpad': vpad,
        'vsep': vsep,
        'width': width,
        'uniform_stretch': uniform_stretch,
        'max_stretched_character': max_stretched_character
    }

    ######################################################################
    # axes_style

    # Set style sheet:
    if style_sheet is not None:
        plt.style.use(style_sheet)

    # Modify ylim and ylabel according to logo_type
    if logo_type == 'counts':
        ymax = matrix.values.sum(axis=1).max()
        if ylim is None:
            ylim = [0, ymax]
        if ylabel is None and axes_type != 'naked':
            ylabel = 'counts'
    elif logo_type == 'probability':
        if ylim is None:
            ylim = [0, 1]
        if ylabel is None and axes_type != 'naked':
            ylabel = 'probability'
    elif logo_type == 'information':
        if ylim is None and (background is None):
            ylim = [0, np.log2(matrix.shape[1])]
        if ylabel is None and axes_type != 'naked':
            ylabel = 'information\n(%s)' % information_units
    elif logo_type == 'enrichment':
        if ylabel is None and axes_type != 'naked':
            ylabel = 'enrichment\n'
            if enrichment_logbase == 2:
                ylabel += '($\log_2$)'
            elif enrichment_logbase == 10:
                ylabel += '($\log_{10})$'
            elif enrichment_logbase == np.e:
                ylabel += '$(\ln)$ '
            else:
                assert False, 'Error: invalid choice of enrichment_logbase=%f'\
                              % enrichment_logbase
    else:
        if ylabel is None:
            ylabel = ''

    # Set ylim (will not be None)
    if ylim is None:
        ymax = (matrix.values * (matrix.values > 0)).sum(axis=1).max()
        ymin = (matrix.values * (matrix.values < 0)).sum(axis=1).min()
        ylim = [ymin, ymax]

    # Set xlim (will not be None)
    if xlim is None:
        xmin = matrix.index.min() - .5
        xmax = matrix.index.max() + .5
        xlim = [xmin, xmax]

    # Set xticks
    if xtick_spacing is None and (axes_type in ['classic', 'everything']):
        xtick_spacing = 1
    if xticks is None and xtick_spacing is not None:
        xticks = [pos for pos in positions if
                  (pos - xtick_anchor) % xtick_spacing == 0.0]

    # If axes_type is specified, make additional modifications
    if axes_type == 'classic':
        if xtick_length is None:
            xtick_length = 0
        if xtick_rotation is None:
            xtick_rotation = 90
        if xlabel is None:
            xlabel = 'position'
        if left_spine is None:
            left_spine = True
        if right_spine is None:
            right_spine = False
        if top_spine is None:
            top_spine = False
        if bottom_spine is None:
            bottom_spine = True
        if show_baseline is None:
            show_baseline = True
        if show_gridlines is None:
            show_gridlines = False

    elif axes_type == 'naked':
        if xticks is None:
            xticks = []
        if xtick_length is None:
            xtick_length = 0
        if xlabel is None:
            xlabel = ''
        if yticks is None:
            yticks = []
        if ylabel is None:
            ylabel = ''
        if left_spine is None:
            left_spine = False
        if right_spine is None:
            right_spine = False
        if top_spine is None:
            top_spine = False
        if bottom_spine is None:
            bottom_spine = False
        if show_baseline is None:
            show_baseline = True
        if show_gridlines is None:
            show_gridlines = False

    elif axes_type == 'rails':
        if xticks is None:
            xticks = []
        if xlabel is None:
            xlabel = ''
        if yticks is None and ylim is not None:
            yticks = ylim
        if left_spine is None:
            left_spine = False
        if right_spine is None:
            right_spine = False
        if top_spine is None:
            top_spine = True
        if bottom_spine is None:
            bottom_spine = True
        if show_baseline is None:
            show_baseline = True
        if show_gridlines is None:
            show_gridlines = False

    elif axes_type == 'everything':
        if xlabel is None:
            xlabel = 'position'
        if left_spine is None:
            left_spine = True
        if right_spine is None:
            right_spine = True
        if top_spine is None:
            top_spine = True
        if bottom_spine is None:
            bottom_spine = True
        if show_baseline is None:
            show_baseline = True
        if show_gridlines is None:
            show_gridlines = False

    elif axes_type == 'vlines':
        if xtick_length is None:
            xtick_length = 0
        if xlabel is None:
            xlabel = 'position'
        if left_spine is None:
            left_spine = False
        if right_spine is None:
            right_spine = False
        if top_spine is None:
            top_spine = False
        if bottom_spine is None:
            bottom_spine = False
        if show_gridlines is None:
            show_gridlines = True
        if gridline_axis is None:
            gridline_axis = 'x'
        if gridline_alpha is None:
            gridline_alpha = .5
        if show_baseline is None:
            show_baseline = True

    # If showing binary yaxis, symmetrize ylim and set yticks to +/-
    if show_binary_yaxis:

        # Force set of ylim, yticks, and yticklabels
        y = np.max(np.abs([y for y in ylim]))
        ylim = [-y, y]
        yticks = [.5 * ylim[0], .5 * ylim[1]]
        yticklabels = ['$-$', '$+$']
        if ytick_length is None:
            ytick_length = 0

    # Set label rotation
    if xtick_rotation is None:
        xtick_rotation = 0
    if ytick_rotation is None:
        ytick_rotation = 0

    if title is None:
        title = ''

    # Default font for all axes elements
    axes_fontdict = {
        'fname': axes_fontfile,
        'family': axes_fontfamily,
        'weight': axes_fontweight,
        'style': axes_fontstyle,
        'size': axes_fontsize,
    }
    axes_fontdict = remove_none_from_dict(axes_fontdict)

    # Font for x and y axis tickmarks
    tick_fontdict = {
        'fname': tick_fontfile,
        'family': tick_fontfamily,
        'weight': tick_fontweight,
        'style': tick_fontstyle,
        'size': tick_fontsize,
    }
    tick_fontdict = remove_none_from_dict(tick_fontdict)
    tick_fontdict = dict(axes_fontdict, **tick_fontdict)
    tick_fontproperties = FontProperties(**tick_fontdict)

    # Font for x and y axis labels
    label_fontdict = {
        'fname': label_fontfile,
        'family': label_fontfamily,
        'weight': label_fontweight,
        'style': label_fontstyle,
        'size': label_fontsize,
    }
    label_fontdict = remove_none_from_dict(label_fontdict)
    label_fontdict = dict(axes_fontdict, **label_fontdict)
    label_fontproperties = FontProperties(**label_fontdict)

    # Font for title
    title_fontdict = {
        'fname': title_fontfile,
        'family': title_fontfamily,
        'weight': title_fontweight,
        'style': title_fontstyle,
        'size': title_fontsize,
    }
    title_fontdict = remove_none_from_dict(title_fontdict)
    title_fontdict = dict(axes_fontdict, **title_fontdict)
    title_fontproperties = FontProperties(**title_fontdict)

    # Gridline styling
    gridline_dict = {
        'axis': gridline_axis,
        'alpha': gridline_alpha,
        'color': gridline_color,
        'linewidth': gridline_width,
        'linestyle': gridline_style,
        'visible': show_gridlines,
    }
    gridline_dict = remove_none_from_dict(gridline_dict)

    # Set baseline defaults
    if baseline_color is None:
        baseline_color = mpl.rcParams['axes.edgecolor']
    if baseline_alpha is None:
        baseline_alpha = 1
    if baseline_width is None:
        baseline_width = mpl.rcParams['axes.linewidth']
    if baseline_style is None:
        baseline_style = '-'

    # Baseline styling
    baseline_dict = {
        'color': baseline_color,
        'alpha': baseline_alpha,
        'linewidth': baseline_width,
        'linestyle': baseline_style,
    }

    # Set vlines defaults
    if vline_color is None:
        vline_color = mpl.rcParams['axes.edgecolor']
    if vline_alpha is None:
        vline_alpha = 1
    if vline_width is None:
        vline_width = mpl.rcParams['axes.linewidth']
    if vline_style is None:
        vline_style = '-'

    # vlines styling
    vline_dict = {
        'color': vline_color,
        'alpha': vline_alpha,
        'linewidth': vline_width,
        'linestyle': vline_style,
    }

    # Set axes_style dictionary
    axes_style = {
        'show_binary_yaxis': show_binary_yaxis,
        'show_baseline': show_baseline,
        'baseline_dict': baseline_dict,
        'vline_positions': vline_positions,
        'vline_dict': vline_dict,
        'title': title,
        'ylim': ylim,
        'yticks': yticks,
        'yticklabels': yticklabels,
        'ylabel': ylabel,
        'xlim': xlim,
        'xticks': xticks,
        'xticklabels': xticklabels,
        'xlabel': xlabel,
        'left_spine': left_spine,
        'right_spine': right_spine,
        'top_spine': top_spine,
        'bottom_spine': bottom_spine,
        'xtick_length': xtick_length,
        'xtick_rotation': xtick_rotation,
        'xtick_format': xtick_format,
        'ytick_length': ytick_length,
        'ytick_rotation': ytick_rotation,
        'ytick_format': ytick_format,
        'font_dict': axes_fontdict.copy(),
        'tick_fontproperties': tick_fontproperties,
        'label_fontproperties': label_fontproperties,
        'title_fontproperties': title_fontproperties,
        'show_gridlines': show_gridlines,
        'gridline_dict': gridline_dict,
        'use_tightlayout': use_tightlayout,
    }

    ######################################################################
    # Create Logo instance
    logo = Logo(matrix=matrix,
                highlight_sequence=highlight_sequence,
                fixedchar_dict=fixedchar_dict,
                font_properties=font_properties,
                character_style=character_style,
                highlight_style=highlight_style,
                fixedchar_style=fixedchar_style,
                placement_style=placement_style,
                axes_style=axes_style)

    # Decorate logo
    logo.logo_type = logo_type
    logo.background = background
    logo.bg_mat = bg_mat

    ######################################################################
    # Optionally draw logo

    # Set RC parameters
    for key, value in rcparams.items():
        mpl.rcParams[key] = value

    # Set default figsize
    if figsize is None:
        figsize = [default_fig_width, default_fig_height_per_line]

    # If user specifies a figure size, make figure and axis,
    # draw logo, then return all three
    if draw_now:

        fig, ax = plt.subplots(figsize=figsize)
        logo.draw(ax)

        if use_tightlayout:
            plt.tight_layout()
            plt.draw()

        if save_to_file:
            fig.savefig(save_to_file, dpi=dpi)
        plt.draw()

        logo.ax = ax
        logo.fig = fig

    # Otherwise, just return logo to user without drawing
    else:
        logo.ax = None
        logo.fig = None

    # Return logo to user
    return logo


# Document make_logo
document_function(make_logo, 'make_logo_arguments.txt')