export const cleanRut = (rut) => {
    return typeof rut === 'string' ? rut.replace(/^0+|[^0-9kK]+/g, '').toUpperCase() : '';
};

export const validateRut = (rut) => {
    if (!rut) return false;

    const clean = cleanRut(rut);
    if (clean.length < 2) return false;

    const body = clean.slice(0, -1);
    const dv = clean.slice(-1);

    if (!/^\d+$/.test(body)) return false;

    let suma = 0;
    let multiplo = 2;

    for (let i = body.length - 1; i >= 0; i--) {
        suma += parseInt(body.charAt(i)) * multiplo;
        multiplo = multiplo < 7 ? multiplo + 1 : 2;
    }

    const dvCalc = 11 - (suma % 11);
    const dvEsperado = dvCalc === 11 ? '0' : dvCalc === 10 ? 'K' : dvCalc.toString();

    return dv === dvEsperado;
};

export const formatRut = (rut) => {
    if (!rut) return '';

    const clean = cleanRut(rut);
    if (clean.length <= 1) return clean;

    const body = clean.slice(0, -1);
    const dv = clean.slice(-1);

    let formattedBody = '';
    for (let i = body.length - 1, j = 0; i >= 0; i--, j++) {
        formattedBody = body.charAt(i) + (j > 0 && j % 3 === 0 ? '.' : '') + formattedBody;
    }

    return `${formattedBody}-${dv}`;
};
