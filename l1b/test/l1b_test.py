import os

import numpy as np
import xarray as xr


# ---------------------------------------------------------------------
# CARPETAS
# ---------------------------------------------------------------------

# Archivos generados por la profesora
CARPETA_PROFE = (
    r"C:\Users\santi\Desktop\MSTR-2\PODT\EODP_TER_2021"
    r"\EODP-TS-L1B\output"
)

# Archivos generados por ti
CARPETA_SANTI = (
    r"C:\Users\santi\Desktop\MSTR-2\PODT\EODP_TER_2021"
    r"\EODP-TS-L1B\output_santi"
)


# ---------------------------------------------------------------------
# TOLERANCIAS NUMÉRICAS
# ---------------------------------------------------------------------

# Se permiten diferencias decimales muy pequeñas.
RTOL = 1e-5
ATOL = 1e-8


def comparar_archivos(ruta_santi, ruta_profe):
    """
    Compara dos archivos NetCDF.

    Comprueba:
    - Dimensiones
    - Variables
    - Forma de cada variable
    - Valores numéricos
    - Valores no numéricos
    """

    nombre_archivo = os.path.basename(ruta_santi)

    print("\n" + "=" * 80)
    print(f"COMPARANDO: {nombre_archivo}")
    print("=" * 80)

    archivo_correcto = True

    try:
        with (
            xr.open_dataset(ruta_santi) as ds_santi,
            xr.open_dataset(ruta_profe) as ds_profe
        ):

            # ---------------------------------------------------------
            # 1. COMPARAR DIMENSIONES GENERALES
            # ---------------------------------------------------------

            dimensiones_santi = dict(ds_santi.sizes)
            dimensiones_profe = dict(ds_profe.sizes)

            if dimensiones_santi == dimensiones_profe:
                print("OK: dimensiones generales iguales")
            else:
                archivo_correcto = False
                print("ERROR: dimensiones generales diferentes")
                print(f"  Santi: {dimensiones_santi}")
                print(f"  Profe: {dimensiones_profe}")

            # ---------------------------------------------------------
            # 2. COMPARAR VARIABLES EXISTENTES
            # ---------------------------------------------------------

            variables_santi = set(ds_santi.variables)
            variables_profe = set(ds_profe.variables)

            solo_santi = variables_santi - variables_profe
            solo_profe = variables_profe - variables_santi

            if not solo_santi and not solo_profe:
                print("OK: aparecen las mismas variables")
            else:
                archivo_correcto = False
                print("ERROR: no aparecen las mismas variables")

                if solo_santi:
                    print("  Variables que solamente tienes tú:")
                    for variable in sorted(solo_santi):
                        print(f"    - {variable}")

                if solo_profe:
                    print("  Variables que solamente tiene la profesora:")
                    for variable in sorted(solo_profe):
                        print(f"    - {variable}")

            # ---------------------------------------------------------
            # 3. COMPARAR VARIABLES COMUNES
            # ---------------------------------------------------------

            variables_comunes = sorted(
                variables_santi & variables_profe
            )

            for variable in variables_comunes:
                datos_santi = ds_santi[variable]
                datos_profe = ds_profe[variable]

                valores_santi = datos_santi.values
                valores_profe = datos_profe.values

                # Comparar dimensiones de la variable
                if datos_santi.dims != datos_profe.dims:
                    archivo_correcto = False
                    print(f"ERROR en '{variable}': dimensiones diferentes")
                    print(f"  Santi: {datos_santi.dims}")
                    print(f"  Profe: {datos_profe.dims}")
                    continue

                # Comparar forma de los datos
                if valores_santi.shape != valores_profe.shape:
                    archivo_correcto = False
                    print(f"ERROR en '{variable}': formas diferentes")
                    print(f"  Santi: {valores_santi.shape}")
                    print(f"  Profe: {valores_profe.shape}")
                    continue

                es_numerica_santi = np.issubdtype(
                    valores_santi.dtype,
                    np.number
                )

                es_numerica_profe = np.issubdtype(
                    valores_profe.dtype,
                    np.number
                )

                # -----------------------------------------------------
                # VARIABLES NUMÉRICAS
                # -----------------------------------------------------

                if es_numerica_santi and es_numerica_profe:
                    valores_iguales = np.allclose(
                        valores_santi,
                        valores_profe,
                        rtol=RTOL,
                        atol=ATOL,
                        equal_nan=True
                    )

                    if valores_iguales:
                        print(f"OK: {variable}")
                    else:
                        archivo_correcto = False

                        mascara_diferencias = ~np.isclose(
                            valores_santi,
                            valores_profe,
                            rtol=RTOL,
                            atol=ATOL,
                            equal_nan=True
                        )

                        numero_diferencias = np.count_nonzero(
                            mascara_diferencias
                        )

                        numero_elementos = mascara_diferencias.size

                        valores_santi_float = valores_santi.astype(float)
                        valores_profe_float = valores_profe.astype(float)

                        diferencia_absoluta = np.abs(
                            valores_santi_float - valores_profe_float
                        )

                        if np.all(np.isnan(diferencia_absoluta)):
                            diferencia_maxima = np.nan
                            diferencia_media = np.nan
                        else:
                            diferencia_maxima = np.nanmax(
                                diferencia_absoluta
                            )
                            diferencia_media = np.nanmean(
                                diferencia_absoluta
                            )

                        porcentaje_diferencias = (
                            numero_diferencias / numero_elementos
                        ) * 100

                        print(f"ERROR en '{variable}': valores diferentes")
                        print(
                            f"  Elementos diferentes: "
                            f"{numero_diferencias}/{numero_elementos}"
                        )
                        print(
                            f"  Porcentaje diferente: "
                            f"{porcentaje_diferencias:.4f}%"
                        )
                        print(
                            f"  Diferencia máxima: {diferencia_maxima}"
                        )
                        print(
                            f"  Diferencia media: {diferencia_media}"
                        )

                # -----------------------------------------------------
                # VARIABLES NO NUMÉRICAS
                # -----------------------------------------------------

                else:
                    try:
                        valores_iguales = np.array_equal(
                            valores_santi,
                            valores_profe,
                            equal_nan=True
                        )
                    except TypeError:
                        valores_iguales = np.array_equal(
                            valores_santi,
                            valores_profe
                        )

                    if valores_iguales:
                        print(f"OK: {variable}")
                    else:
                        archivo_correcto = False
                        print(
                            f"ERROR en '{variable}': "
                            f"valores no numéricos diferentes"
                        )

    except Exception as error:
        archivo_correcto = False
        print(f"ERROR al abrir o comparar el archivo: {error}")

    # -------------------------------------------------------------
    # RESULTADO DEL ARCHIVO
    # -------------------------------------------------------------

    if archivo_correcto:
        print(f"\nRESULTADO: {nombre_archivo} COINCIDE")
    else:
        print(f"\nRESULTADO: {nombre_archivo} TIENE DIFERENCIAS")

    return archivo_correcto


def main():
    # Tipos de archivos:
    # - Con "_eq"
    # - Sin "_eq"
    tipos_archivo = [
        "l1b_toa_eq_VNIR",
        "l1b_toa_VNIR"
    ]

    resultados = {}

    print("=" * 80)
    print("CROSSVALIDACIÓN DE ARCHIVOS NETCDF")
    print("=" * 80)
    print(f"Carpeta de Santi: {CARPETA_SANTI}")
    print(f"Carpeta profesora: {CARPETA_PROFE}")

    # Comprobar que las carpetas existen
    if not os.path.isdir(CARPETA_SANTI):
        print("\nERROR: no existe la carpeta de Santi:")
        print(CARPETA_SANTI)
        return

    if not os.path.isdir(CARPETA_PROFE):
        print("\nERROR: no existe la carpeta de la profesora:")
        print(CARPETA_PROFE)
        return

    # -------------------------------------------------------------
    # COMPARAR LOS 8 ARCHIVOS
    # -------------------------------------------------------------

    for tipo in tipos_archivo:
        for numero in range(4):
            nombre = f"{tipo}-{numero}.nc"

            ruta_santi = os.path.join(
                CARPETA_SANTI,
                nombre
            )

            ruta_profe = os.path.join(
                CARPETA_PROFE,
                nombre
            )

            if not os.path.isfile(ruta_santi):
                print("\n" + "=" * 80)
                print(f"NO EXISTE TU ARCHIVO: {nombre}")
                print(f"Ruta buscada: {ruta_santi}")
                resultados[nombre] = False
                continue

            if not os.path.isfile(ruta_profe):
                print("\n" + "=" * 80)
                print(
                    f"NO EXISTE EL ARCHIVO DE LA PROFESORA: {nombre}"
                )
                print(f"Ruta buscada: {ruta_profe}")
                resultados[nombre] = False
                continue

            resultados[nombre] = comparar_archivos(
                ruta_santi,
                ruta_profe
            )

    # -------------------------------------------------------------
    # RESUMEN FINAL
    # -------------------------------------------------------------

    print("\n\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)

    for nombre, coincide in resultados.items():
        if coincide:
            estado = "COINCIDE"
        else:
            estado = "TIENE DIFERENCIAS O NO EXISTE"

        print(f"{nombre}: {estado}")

    numero_correctos = sum(resultados.values())
    numero_total = len(resultados)

    print("-" * 80)
    print(f"Archivos correctos: {numero_correctos}/{numero_total}")

    if numero_total == 8 and all(resultados.values()):
        print(
            "\nRESULTADO FINAL: los 8 archivos coinciden "
            "con los de la profesora."
        )
    else:
        print(
            "\nRESULTADO FINAL: hay archivos con diferencias "
            "o archivos inexistentes."
        )


if __name__ == "__main__":
    main()

# PLOT FROM YOUR OUTPUTS THE EQUALISED OUTPUT VERSUS NOT EQUALISED VERSUS THE TRUTH


import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt


# ============================================================
# RUTAS
# ============================================================

BASE = (
    r"C:\Users\santi\Desktop\MSTR-2\PODT"
    r"\EODP_TER_2021\EODP-TS-L1B"
)

RUTA_EQ = os.path.join(
    BASE,
    "output_santi",
    "l1b_toa_VNIR-0.nc"
)

RUTA_NO_EQ = os.path.join(
    BASE,
    "output_santi_noteq",
    "l1b_toa_VNIR-0.nc"
)

RUTA_TRUTH = os.path.join(
    BASE,
    "input",
    "ism_toa_isrf_VNIR-0.nc"
)

RUTA_PNG = os.path.join(
    BASE,
    "output_santi",
    "comparison_VNIR-0_row50_nalt50.png"
)


# ============================================================
# VALORES SOLICITADOS
# ============================================================

ROW = 50
NALT = 50


# ============================================================
# LEER UN PERFIL
# ============================================================

def leer_perfil(ruta):
    with xr.open_dataset(ruta) as ds:

        if "toa" not in ds:
            raise ValueError(
                f"No se encuentra la variable 'toa' en:\n{ruta}"
            )

        toa = np.asarray(ds["toa"].values)

        print(
            f"{os.path.basename(ruta)}: "
            f"dimensiones={ds['toa'].dims}, forma={toa.shape}"
        )

        if toa.shape != (100, 150):
            raise ValueError(
                f"Se esperaba una matriz (100, 150), "
                f"pero se ha encontrado {toa.shape}"
            )

        # NALT=50 y todos los píxeles ACT
        perfil = toa[NALT, :]

        return perfil


# ============================================================
# COMPROBAR ARCHIVOS
# ============================================================

for ruta in (RUTA_EQ, RUTA_NO_EQ, RUTA_TRUTH):
    if not os.path.isfile(ruta):
        raise FileNotFoundError(
            f"No se encuentra el archivo:\n{ruta}"
        )


# ============================================================
# EXTRAER LOS TRES PERFILES
# ============================================================

toa_eq = leer_perfil(RUTA_EQ)
toa_no_eq = leer_perfil(RUTA_NO_EQ)
toa_truth = leer_perfil(RUTA_TRUTH)

act = np.arange(150)


# ============================================================
# CREAR GRÁFICA
# ============================================================

plt.figure(figsize=(12, 6))

plt.plot(
    act,
    toa_eq,
    color="black",
    linewidth=1.5,
    label="TOA L1B with eq"
)

plt.plot(
    act,
    toa_no_eq,
    color="red",
    linewidth=1.2,
    label="TOA L1B no eq"
)

plt.plot(
    act,
    toa_truth,
    color="blue",
    linewidth=1.5,
    label="TOA after the ISRF"
)

plt.title(
    f"Effect of the Equalization for VNIR-0 "
    f"(row={ROW}, nalt={NALT})"
)

plt.xlabel("ACT pixel [-]")
plt.ylabel("TOA [mW/m²/sr]")

plt.grid(True, alpha=0.5)
plt.legend()
plt.tight_layout()


# ============================================================
# GUARDAR PNG
# ============================================================

plt.savefig(
    RUTA_PNG,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

print("\nGráfica creada correctamente.")
print(f"Row seleccionada: {ROW}")
print(f"NALT seleccionado: {NALT}")
print(f"Imagen guardada en:\n{RUTA_PNG}")


# TRUTH = EODP-TS-L1B\input\ism_toa_isrf_VNIR-0.nc


# row 50 nault 50 eq not eq and the truth (input/ism_toa_isrf_band.nc) and explain what we see there