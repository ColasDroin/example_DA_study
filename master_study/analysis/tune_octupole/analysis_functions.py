import os
import shutil

import matplotlib
import matplotlib.pyplot as plt
import matplotlib_inline
import numpy as np
import qrcode
import seaborn as sns
import yaml
from scipy.ndimage.filters import gaussian_filter


def apply_heatmap_style():
    plt.style.use("ggplot")
    matplotlib.rcParams["mathtext.fontset"] = "cm"
    matplotlib.rcParams["font.family"] = "STIXGeneral"
    # Not italized latex
    matplotlib.rcParams["mathtext.default"] = "regular"
    matplotlib.rcParams["font.weight"] = "light"
    matplotlib_inline.backend_inline.set_matplotlib_formats("retina")


def apply_other_style():
    # Apply better style
    sns.set_theme(style="whitegrid")
    custom_params = {"axes.spines.right": False, "axes.spines.top": False}
    sns.set_theme(style="ticks", rc=custom_params)
    # sns.set(font='Adobe Devanagari')
    sns.set_context("paper", font_scale=1, rc={"lines.linewidth": 0.5, "grid.linewidth": 0.3})

    matplotlib.rcParams["mathtext.fontset"] = "cm"
    matplotlib.rcParams["font.family"] = "STIXGeneral"
    # Not italized latex
    matplotlib.rcParams["mathtext.default"] = "regular"
    matplotlib.rcParams["font.weight"] = "light"


# To add QR codes to plot
def add_QR_code(fig, link):
    # Add QR code pointing to the github repository
    qr = qrcode.QRCode(
        # version=None,
        box_size=10,
        border=1,
    )
    qr.add_data(link)
    qr.make(fit=False)
    im = qr.make_image(fill_color="black", back_color="transparent")
    newax = fig.add_axes([0.9, 0.9, 0.05, 0.05], anchor="NE", zorder=1)
    newax.imshow(im, resample=False, interpolation="none", filternorm=False)
    # Add link below qrcode
    newax.plot([0, 0], [0, 0], color="white", label="link")
    text = newax.annotate(
        "lin",
        xy=(0, 300),
        xytext=(0, 300),
        fontsize=30,
        url=link,
        bbox=dict(color="white", alpha=1e-6, url=link),
        alpha=0,
    )
    # Hide X and Y axes label marks
    newax.xaxis.set_tick_params(labelbottom=False)
    newax.yaxis.set_tick_params(labelleft=False)
    # Hide X and Y axes tick marks
    newax.set_xticks([])
    newax.set_yticks([])
    newax.set_axis_off()

    return fig


# Function to convert floats to scientific latex format
def latex_float(f):
    float_str = "{0:.3g}".format(f)
    if "e" in float_str:
        base, exponent = float_str.split("e")
        return r"${0} \times 10^{{{1}}}$".format(base, int(exponent))
    else:
        return float_str


def load_config(config_path):
    # Read configuration file
    with open(config_path, "r") as fid:
        config = yaml.safe_load(fid)
    return config


def get_title_from_conf(
    conf_mad,
    conf_collider=None,
    type_crossing=None,
    betx=None,
    bety=None,
    Nb=True,
    levelling="",
    CC=False,
    display_intensity=True,
    phase_knob=None,
    octupoles=None,
    LHC_version=None,
    name_filling_scheme=None,
    emittance=None,
    chroma=None,
    sigma_z=None,
):
    # LHC version
    if LHC_version is not None:
        LHC_version = LHC_version
    else:
        try:
            LHC_version = conf_mad["links"]["acc-models-lhc"].split("modules/")[1]
            if LHC_version == "hllhc15":
                LHC_version = "HL-LHC v1.5"
            elif LHC_version == "hllhc16":
                LHC_version = "HL-LHC v1.6"
            elif LHC_version == "2023":
                LHC_version = "Injection (runIII 2023)"
        except:
            LHC_version = conf_mad["links"]["acc-models-lhc"].split("optics/")[1]
            if LHC_version == "runIII":
                LHC_version = "Run III"
            if "2023" in conf_mad["optics_file"]:
                LHC_version = LHC_version + " (2023)"
            elif "2024" in conf_mad["optics_file"]:
                LHC_version = LHC_version + " (2024)"

    # Energy
    energy_value = float(conf_mad["beam_config"]["lhcb1"]["beam_energy_tot"]) / 1000
    energy = f"$E = {{{energy_value:.2f}}}$ $TeV$"

    if conf_collider is not None:
        # Levelling
        levelling = levelling
        if levelling != "":
            levelling += " ."

        # Bunch number
        bunch_number_value = conf_collider["config_beambeam"]["mask_with_filling_pattern"][
            "i_bunch_b1"
        ]
        bunch_number = f"Bunch {bunch_number_value}"

        # Crab cavities
        if CC:
            if "on_crab1" in conf_collider["config_knobs_and_tuning"]["knob_settings"]:
                if (
                    conf_collider["config_knobs_and_tuning"]["knob_settings"]["on_crab1"]
                    is not None
                ):
                    crab_cavities = "CC ON. "
                else:
                    crab_cavities = "CC OFF. "
            else:
                crab_cavities = "NO CC. "
        else:
            crab_cavities = ""

        # Bunch intensity
        if Nb:
            try:
                bunch_intensity_value = conf_collider["config_beambeam"][
                    "num_particles_per_bunch_after_optimization"
                ]
            except:
                bunch_intensity_value = conf_collider["config_beambeam"]["num_particles_per_bunch"]
            bunch_intensity = (
                f"$N_b \simeq $" + latex_float(float(bunch_intensity_value)) + " ppb, "
            )
        else:
            bunch_intensity = ""

        try:
            luminosity_value_1_5 = conf_collider["config_beambeam"][
                "luminosity_ip1_5_after_optimization"
            ]
            luminosity_value_2 = conf_collider["config_beambeam"][
                "luminosity_ip2_after_optimization"
            ]
            luminosity_value_8 = conf_collider["config_beambeam"][
                "luminosity_ip8_after_optimization"
            ]
        except:
            luminosity_value_1_5 = None
            luminosity_value_2 = None
            luminosity_value_8 = None
        if luminosity_value_1_5 is not None:
            luminosity_1_5 = (
                f"$L_{{1/5}} = $" + latex_float(float(luminosity_value_1_5)) + "cm$^{-2}$s$^{-1}$, "
            )
            luminosity_2 = (
                f"$L_{{2}} = $" + latex_float(float(luminosity_value_2)) + "cm$^{-2}$s$^{-1}$, "
            )
            luminosity_8 = (
                f"$L_{{8}} = $" + latex_float(float(luminosity_value_8)) + "cm$^{-2}$s$^{-1}$"
            )
        else:
            luminosity_1_5 = ""
            luminosity_2 = ""
            luminosity_8 = ""

        # Beta star # ! Manually encoded for now
        if "flathv" in conf_mad["optics_file"]:
            bet1 = r"$\beta^{*}_{y,1}$"
            bet2 = r"$\beta^{*}_{x,1}$"
        # If betas are given, we always define betx first, whatever the crossing
        elif "flatvh" in conf_mad["optics_file"] or (betx is not None and bety is not None):
            bet1 = r"$\beta^{*}_{x,1}$"
            bet2 = r"$\beta^{*}_{y,1}$"
        if betx is not None and bety is not None:
            beta = bet1 + f"$= {{{betx}}}$" + " m, " + bet2 + f"$= {{{bety}}}$" + " m"
        else:
            if "75_180" in conf_mad["optics_file"]:
                beta = bet1 + r"$= 7.5$ cm, " + bet2 + r"$= 18$ cm"
            elif "500_1000" in conf_mad["optics_file"]:
                beta = bet1 + r"$= 0.5$ m, " + bet2 + r"$= 1$ m"
            else:
                beta = bet1 + r"$= 0.1$ m, " + bet2 + r"$= 0.1$ m"
                # raise ValueError("Optics configuration not automatized yet, or betas not provided")

        # Crossing angle at IP1/5
        if "flathv" in conf_mad["optics_file"] or type_crossing == "flathv":
            phi_1 = r"$\Phi/2_{1(H)}$"
            phi_5 = r"$\Phi/2_{5(V)}$"
        elif "flatvh" in conf_mad["optics_file"] or type_crossing == "flatvh":
            phi_1 = r"$\Phi/2_{1(V)}$"
            phi_5 = r"$\Phi/2_{5(H)}$"
        else:
            phi_1 = r"$\Phi/2_{1(H)}$"
            phi_5 = r"$\Phi/2_{5(V)}$"
        # else:
        #     raise ValueError("Optics configuration not automatized yet")
        xing_value_IP1 = (
            np.nan
        )  # conf_collider["config_knobs_and_tuning"]["knob_settings"]["on_x1"]
        xing_IP1 = phi_1 + f"$= {{{xing_value_IP1:.0f}}}$" + f" $\mu rad$"

        xing_value_IP5 = (
            np.nan
        )  # conf_collider["config_knobs_and_tuning"]["knob_settings"]["on_x5"]
        xing_IP5 = phi_5 + f"$= {{{xing_value_IP5:.0f}}}$" + f" $\mu rad$"

        # Bunch length
        if sigma_z is None:
            bunch_length_value = conf_collider["config_beambeam"]["sigma_z"] * 100
            bunch_length = f"$\sigma_{{z}} = {{{bunch_length_value}}}$ $cm$, "
        else:
            bunch_length = sigma_z

        # Crosing angle at IP8
        xing_value_IP8h = (
            np.nan
        )  # conf_collider["config_knobs_and_tuning"]["knob_settings"]["on_x8h"]
        xing_value_IP8v = (
            np.nan
        )  # conf_collider["config_knobs_and_tuning"]["knob_settings"]["on_x8v"]
        if xing_value_IP8v != 0 and xing_value_IP8h == 0:
            xing_IP8 = r"$\Phi/2_{8,V}$" + f"$= {{{xing_value_IP8v:.0f}}}$ $\mu rad$"
        elif xing_value_IP8v == 0 and xing_value_IP8h != 0:
            xing_IP8 = r"$\Phi/2_{8,H}$" + f"$= {{{xing_value_IP8h:.0f}}}$ $\mu rad$"
        else:
            xing_IP8 = "no crossing"
            # raise ValueError("Optics configuration not automatized yet")

        # Crosing angle at IP2
        try:
            xing_value_IP2h = (
                np.nan
            )  # conf_collider["config_knobs_and_tuning"]["knob_settings"]["on_x2h"]
            xing_value_IP2v = (
                np.nan
            )  # conf_collider["config_knobs_and_tuning"]["knob_settings"]["on_x2v"]
        except:
            xing_value_IP2h = 0
            xing_value_IP2v = conf_collider["config_knobs_and_tuning"]["knob_settings"]["on_x2"]
        if xing_value_IP2v != 0 and xing_value_IP2h == 0:
            xing_IP2 = r"$\Phi/2_{2,V}$" + f"$= {{{xing_value_IP2v:.0f}}}$ $\mu rad$"
        elif xing_value_IP8v == 0 and xing_value_IP8h != 0:
            xing_IP2 = r"$\Phi/2_{2,H}$" + f"$= {{{xing_value_IP2h:.0f}}}$ $\mu rad$"
        else:
            xing_IP2 = "no crossing"
            # raise ValueError("Optics configuration not automatized yet")

        # Polarity IP 2 and 8
        polarity_value_IP2 = conf_collider["config_knobs_and_tuning"]["knob_settings"][
            "on_alice_normalized"
        ]
        polarity_value_IP8 = conf_collider["config_knobs_and_tuning"]["knob_settings"][
            "on_lhcb_normalized"
        ]
        polarity = f"$polarity$ $IP_{{2/8}} = {{{polarity_value_IP2}}}/{{{polarity_value_IP8}}}$"

        # Normalized emittance
        if emittance is None:
            emittance_value = round(conf_collider["config_beambeam"]["nemitt_x"] / 1e-6, 2)
        else:
            emittance_value = emittance
        emittance = f"$\epsilon_{{n}} = {{{emittance_value}}}$ $\mu m$"

        # Chromaticity
        if chroma is None:
            chroma_value = conf_collider["config_knobs_and_tuning"]["dqx"]["lhcb1"]
            chroma = r"$Q'$" + f"$= {{{chroma_value}}}$, "
        else:
            chroma = chroma

        # Intensity
        if display_intensity:
            if octupoles is not None:
                intensity_value = octupoles
            else:
                intensity_value = conf_collider["config_knobs_and_tuning"]["knob_settings"][
                    "i_oct_b1"
                ]
            intensity = f"$I_{{MO}} = {{{intensity_value}}}$ $A$, "
        else:
            intensity = ""

        # Linear coupling
        coupling_value = conf_collider["config_knobs_and_tuning"]["delta_cmr"]
        coupling = f"$C^- = {{{coupling_value}}}$"

        # Filling scheme
        if name_filling_scheme is None:
            filling_scheme_value = conf_collider["config_beambeam"]["mask_with_filling_pattern"][
                "pattern_fname"
            ].split("filling_scheme/")[1]
            if "12inj" in filling_scheme_value:
                filling_scheme_value = filling_scheme_value.split("12inj")[0] + "12inj"
            filling_scheme = f"{filling_scheme_value}"
        else:
            filling_scheme = name_filling_scheme

        # Phase knob
        if phase_knob is not None:
            phase_change = "phase_change = " + str(phase_knob)
        else:
            phase_change = ""

        title = (
            LHC_version
            + ". "
            + energy
            + ". "
            + levelling
            + crab_cavities
            + bunch_intensity
            # + "\n"
            # + luminosity_1_5
            # + luminosity_2
            # + luminosity_8
            + "\n"
            + beta
            + ", "
            + polarity
            + ", "
            + phase_change
            + "\n"
            # + xing_IP1
            # + ", "
            # + xing_IP5
            # + ", "
            # + xing_IP2
            # + ", "
            # + xing_IP8
            # + "\n"
            + bunch_length
            # + ", "
            + emittance
            + ", "
            + chroma
            + intensity
            + coupling
            + "\n"
            + filling_scheme
            + ". "
            + bunch_number
            + "."
        )
    else:
        title = LHC_version + ". " + energy + ". "
    return title


def plot_heatmap(
    df_to_plot,
    study_name,
    link=None,
    plot_contours=True,
    conf_mad=None,
    conf_collider=None,
    type_crossing=None,
    betx=None,
    bety=None,
    Nb=True,
    levelling="",
    CC=False,
    xlabel="Horizontal tune " + r"$Q_x$",
    ylabel="Vertical tune " + r"$Q_y$",
    symmetric=True,
    mask_lower_triangle=True,
    plot_diagonal_lines=True,
    xaxis_ticks_on_top=True,
    title=None,
    add_vline=None,
    display_intensity=True,
    vmin=4.5,
    vmax=7.5,
    extended_diagonal=False,
    prevent_mask=False,
    small_delta_diagonal=False,
    phase_knob=None,
    octupoles=None,
    LHC_version=None,
    name_filling_scheme=None,
    label_colormap="Minimum DA (" + r"$\sigma$" + ")",
):
    # Get numpy array from dataframe
    data_array = df_to_plot.to_numpy()

    # Define colormap and set NaNs to white
    cmap = matplotlib.cm.get_cmap("coolwarm_r", 50)
    cmap.set_bad("w")

    # Build heatmap, with inverted y axis
    fig, ax = plt.subplots()
    im = ax.imshow(data_array, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.invert_yaxis()

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(df_to_plot.columns))[::2], labels=df_to_plot.columns[::2])
    ax.set_yticks(np.arange(len(df_to_plot.index))[::2], labels=df_to_plot.index[::2])

    # Loop over data dimensions and create text annotations.
    for i in range(len(df_to_plot.index)):
        for j in range(len(df_to_plot.columns)):
            if data_array[i, j] >= vmax:
                val = r"$\geq $" + str(vmax)
            elif data_array[i, j] <= vmin:
                val = r"$\leq $" + str(vmin)
            else:
                val = f"{data_array[i, j]:.1f}"
            text = ax.text(j, i, val, ha="center", va="center", color="white", fontsize=4)

    # Smooth data for contours
    # make the matrix symmetric by replacing the lower triangle with the upper triangle
    data_smoothed = np.copy(data_array)
    data_smoothed[np.isnan(data_array)] = 0
    if symmetric and not extended_diagonal:
        data_smoothed = data_smoothed + data_smoothed.T - np.diag(data_array.diagonal())
    elif symmetric:
        try:
            # sum the upper and lower triangle, but not the intersection of the two matrices
            intersection = np.zeros_like(data_smoothed)
            for x in range(data_smoothed.shape[0]):
                for y in range(data_smoothed.shape[1]):
                    if np.min((data_smoothed[x, y], data_smoothed[y, x])) == 0.0:
                        intersection[x, y] = 0.0
                    else:
                        intersection[x, y] = data_smoothed[y, x]
            data_smoothed = data_smoothed + data_smoothed.T - intersection
        except:
            print("Did not manage to smooth properly")
    data_smoothed = gaussian_filter(data_smoothed, 0.7)

    # Mask the lower triangle of the smoothed matrix
    if not extended_diagonal and mask_lower_triangle:
        mask = np.tri(data_smoothed.shape[0], k=-1)
        mx = np.ma.masked_array(data_smoothed, mask=mask.T)
    elif extended_diagonal:
        if prevent_mask:
            mx = data_smoothed
        else:
            try:
                mask = np.tri(data_smoothed.shape[0], k=-5)
                mx = np.ma.masked_array(data_smoothed, mask=mask.T)
            except:
                print("Did not manage to mask properly")
                mx = data_smoothed

    else:
        mx = data_smoothed

    # Plot contours if requested
    if plot_contours:
        CSS = ax.contour(
            np.arange(0.5, data_array.shape[1]),
            np.arange(0.5, data_array.shape[0]),
            mx,
            colors="black",
            levels=list(np.arange(3, 6, 0.5)) + list(np.arange(6.5, 10, 0.5)),
            linewidths=0.2,
        )
        ax.clabel(CSS, inline=True, fontsize=6)
        CS2 = ax.contour(
            np.arange(0.5, data_array.shape[1]),
            np.arange(0.5, data_array.shape[0]),
            mx,
            colors="green",
            levels=[6],
            linewidths=1,
        )
        ax.clabel(CS2, inline=1, fontsize=6)

    if plot_diagonal_lines:
        # ! Diagonal lines must be plotted after the contour lines, because of bug in matplotlib
        # ! Careful, depending on how the tunes were defined, may be shifted by 1
        # Diagonal lines
        if extended_diagonal:
            if small_delta_diagonal:
                ax.plot([0, 1000], [1, 1001], color="tab:blue", linestyle="--", linewidth=1)
                ax.plot([0, 1000], [-1, 999], color="tab:blue", linestyle="--", linewidth=1)
            else:
                ax.plot([0, 1000], [5, 1005], color="tab:blue", linestyle="--", linewidth=1)
                ax.plot([0, 1000], [-5, 995], color="tab:blue", linestyle="--", linewidth=1)
            ax.plot([0, 1000], [0, 1000], color="black", linestyle="--", linewidth=1)
        else:
            ax.plot([0, 1000], [1, 1001], color="tab:blue", linestyle="--", linewidth=1)
            ax.plot([0, 1000], [-9, 991], color="tab:blue", linestyle="--", linewidth=1)
            ax.plot([0, 1000], [-4, 996], color="black", linestyle="--", linewidth=1)

    # Define title and axis labels
    if title is None:
        ax.set_title(
            get_title_from_conf(
                conf_mad,
                conf_collider,
                type_crossing=type_crossing,
                betx=betx,
                bety=bety,
                Nb=Nb,
                levelling=levelling,
                CC=CC,
                display_intensity=display_intensity,
                phase_knob=phase_knob,
                octupoles=octupoles,
                LHC_version=LHC_version,
                name_filling_scheme=name_filling_scheme,
            ),
            fontsize=10,
        )
    else:
        ax.set_title(title, fontsize=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(0 - 0.5, data_array.shape[1] - 0.5)
    ax.set_ylim(0 - 0.5, data_array.shape[0] - 0.5)

    # Ticks on top
    if xaxis_ticks_on_top:
        ax.xaxis.tick_top()
    # Rotate the tick labels and set their alignment.
    plt.setp(
        ax.get_xticklabels(), rotation=-30, rotation_mode="anchor"  # , ha="left"
    )  # , rotation_mode="anchor")
    # ax.tick_params(axis='x', which='major', pad=5)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.026, pad=0.04)
    cbar.ax.set_ylabel(label_colormap, rotation=90, va="bottom", labelpad=15)
    plt.grid(visible=None)

    # Add QR code
    if link is not None:
        fig = add_QR_code(fig, link)

    if add_vline is not None:
        plt.axvline(add_vline, color="black", linestyle="--", linewidth=1)
        plt.text(add_vline, 25, r"Bunch intensity $\simeq \beta^*_{2023} = 0.3/0.3$", fontsize=8)

    plt.savefig("plots/output_" + study_name + ".pdf", bbox_inches="tight")
    plt.show()


def copy_study_on_eos(study_name, type_analysis="tune_scan"):
    path_study = "/afs/cern.ch/work/c/cdroin/private/example_DA_study/master_study/"
    path_EOS = "/eos/home-c/cdroin/save_simulations/"
    path_archive = path_EOS + study_name + "/"

    ### Rebuild structue of the study on EOS
    try:
        os.mkdir(path_archive)
    except FileExistsError:
        print("Directory already exists, continue...")

    # # Copy all master jobs
    # shutil.copytree(path_study + "master_jobs",
    #                 path_archive + "master_jobs",
    #                 dirs_exist_ok=True)

    # Copy analysis
    suffix_analysis = f"analysis/{type_analysis}/analysis_" + study_name + ".ipynb"
    path_source_analysis = path_study + suffix_analysis
    path_destination_analysis = path_archive + suffix_analysis
    os.makedirs(os.path.dirname(path_destination_analysis), exist_ok=True)
    shutil.copy(path_source_analysis, path_destination_analysis)

    # Copy scripts to generate and analyse the scan
    suffix_scripts = [
        "001_make_folders_" + study_name + ".py",
    ]
    #  "002_chronjob.py",
    #  "003_postprocessing.py"]
    for suffix in suffix_scripts:
        path_source = path_study + suffix
        path_destination = path_archive + suffix
        shutil.copy(path_source, path_destination)

    # Copy scan
    print("Start copying scan, this may take a while...")
    shutil.copytree(
        path_study + "scans/" + study_name,
        path_archive + "/scans/" + study_name,
        dirs_exist_ok=True,
    )

    return path_archive, path_EOS


def archive_and_clean(path_archive, path_EOS):
    # Convert the archive to a zip file, and export to EOS
    shutil.make_archive(path_archive, "zip", path_EOS, path_archive.split("/")[-1])

    # Delete the folder archive
    shutil.rmtree(path_archive)
