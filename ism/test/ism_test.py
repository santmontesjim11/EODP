import os
import numpy as np
import xarray as xr

CARPETA_PROFE = (
    r"C:\Users\santi\Desktop\MSTR-2\PODT\EODP_TER_2021"
    r"\EODP-TS-ISM\output"
)

CARPETA_SANTI = (
    r"C:\Users\santi\Desktop\MSTR-2\PODT\EODP_TER_2021"
    r"\EODP-TS-ISM\output_santi"
)

tipos = [
    "ism_toa_detection",
    "ism_toa_ds",
    "ism_toa_e",
    "ism_toa_isrf",
    "ism_toa_optical",
    "ism_toa_prnu",
    "ism_toa",
]

for tipo in tipos:
    for numero in range(4):
        nombre = f"{tipo}_VNIR-{numero}.nc"
        ruta_profe = os.path.join(CARPETA_PROFE, nombre)
        ruta_santi = os.path.join(CARPETA_SANTI, nombre)

        if not os.path.isfile(ruta_profe) or not os.path.isfile(ruta_santi):
            print(f"{nombre}: FALTA UN ARCHIVO")
            continue

        with xr.open_dataset(ruta_profe) as profe, xr.open_dataset(ruta_santi) as santi:
            coinciden = (
                profe.sizes == santi.sizes
                and set(profe.variables) == set(santi.variables)
            )

            if coinciden:
                for variable in profe.variables:
                    a = profe[variable]
                    b = santi[variable]

                    if a.dims != b.dims or a.shape != b.shape:
                        coinciden = False
                        break

                    if (
                        np.issubdtype(a.dtype, np.number)
                        and np.issubdtype(b.dtype, np.number)
                    ):
                        iguales = np.allclose(
                            a.values, b.values,
                            rtol=1e-5, atol=1e-8, equal_nan=True
                        )
                    else:
                        iguales = np.array_equal(a.values, b.values)

                    if not iguales:
                        coinciden = False
                        break

        print(f"{nombre}: {'COINCIDE' if coinciden else 'NO COINCIDE'}")


# Valores teóricos y leídos en el píxel [50, 75]

from ism.src.detectionPhase import detectionPhase

# Obtener input y auxiliary a partir de tus rutas
carpeta_ism = os.path.dirname(CARPETA_SANTI)
carpeta_input = os.path.join(carpeta_ism, "input")

# Este test está en ism/test/: parents[2] es la raíz del proyecto
from pathlib import Path

carpeta_aux = Path(__file__).resolve().parents[2] / "auxiliary"

modelo = detectionPhase(
    carpeta_aux.as_posix(),
    carpeta_input.replace("\\", "/"),
    CARPETA_SANTI.replace("\\", "/")
)

cfg = modelo.ismConfig
fila, columna = 50, 75


def leer_etapa(prefijo, banda):
    ruta = os.path.join(
        CARPETA_SANTI,
        f"{prefijo}_VNIR-{banda}.nc"
    )

    with xr.open_dataset(ruta) as datos:
        return np.asarray(datos["toa"].values)


for banda in range(4):

    radiancias = leer_etapa("ism_toa_isrf", banda)
    optica = leer_etapa("ism_toa_optical", banda)
    deteccion = leer_etapa("ism_toa_detection", banda)
    salida_dn = leer_etapa("ism_toa", banda)

    radiancia = float(radiancias[fila, columna])
    irradiancia_leida = float(optica[fila, columna])

    # Irradiancia ideal antes de aplicar la MTF
    irradiancia = (
            cfg.Tr * radiancia
            * np.pi / 4
            * (cfg.D / cfg.f) ** 2
    )

    # Fotones: partir de la irradiancia que ya incluye la MTF
    energia = (
            irradiancia_leida * 1e-3
            * cfg.pix_size ** 2
            * cfg.t_int
    )

    energia_foton = (
            modelo.constants.h_planck
            * modelo.constants.speed_light
            / cfg.wv[banda]
    )

    fotones = energia / energia_foton

    # Electrones y saturación del detector
    electrones = min(fotones * cfg.QE, cfg.FWC)

    # Misma semilla y orden de números aleatorios que vuestro ISM
    generador = np.random.RandomState(cfg.seed)
    ncolumnas = optica.shape[1]

    if cfg.apply_prnu:
        prnu = generador.standard_normal(ncolumnas) * cfg.kprnu
        electrones *= 1 + prnu[columna]

    if cfg.apply_dark_signal:
        sd = (
                cfg.ds_A_coeff
                * (cfg.T / cfg.Tref) ** 3
                * np.exp(
            -cfg.ds_B_coeff * (1 / cfg.T - 1 / cfg.Tref)
        )
        )

        dsnu = np.abs(
            generador.standard_normal(ncolumnas) * cfg.kdsnu
        )

        electrones += sd * (1 + dsnu[columna])

    # Vuestra implementación solo modifica la columna 5
    if cfg.apply_bad_dead and columna == 5:
        electrones *= 1 - cfg.bad_pix_red

    # Electrones -> voltios
    voltios = electrones * cfg.OCF * cfg.ADC_gain

    # Voltios -> DN, tal como lo implementasteis
    max_dn = 2 ** cfg.bit_depth - 1

    dn = int(np.clip(
        np.round(
            voltios / (cfg.max_voltage - cfg.min_voltage)
            * max_dn
        ),
        0,
        max_dn
    ))

    resultados = [
        ("Radiancia [mW/m²/sr]", None, radiancia),
        ("Irradiancia [mW/m²]", irradiancia, irradiancia_leida),
        ("Fotones [ph]", fotones, None),
        ("Electrones [e-]", electrones, float(deteccion[fila, columna])),
        ("Voltios [V]", voltios, None),
        ("DN", dn, float(salida_dn[fila, columna])),
    ]

    print(f"\nVNIR-{banda} — Píxel [{fila}, {columna}]")

    for etapa, calculado, leido in resultados:
        texto_calculado = (
            "Dato de partida"
            if calculado is None
            else f"{calculado:.6f}"
        )

        texto_leido = (
            "Sin archivo"
            if leido is None
            else f"{leido:.6f}"
        )

        print(
            f"{etapa}: calculado = {texto_calculado} | "
            f"leído = {texto_leido}"
        )
