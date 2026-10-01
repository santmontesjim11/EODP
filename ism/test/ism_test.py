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


