const THEME_TYPES = ["type-dark", "type-light"];


/**
 * Set some cookie value
 * @param {string} name Cookie name
 * @param {string} value Cookie value
 */
function setCookie(name, value) {
    document.cookie = `${name}=${value}; path=/; expires=Tue, 19 Jan 2038 03:14:07 GMT`;
}


/**
 * Set some boolean ("1" or "") cookie value
 * @param {string} name Cookie name
 * @param {boolean} value Cookie value
 */
function setBooleanCookie(name, value) {
    setCookie(name, value ? "1" : "");
}


function invertTheme() {
    let body = document.body.classList;
    let button = document.getElementById("invert-theme-button").classList;

    setBooleanCookie("type_light", body.contains(THEME_TYPES[0]));

    THEME_TYPES.forEach(i => {
        body.toggle(i);
        button.toggle(i);
    })
}


/**
 * Set color theme and type
 * @param {string} themeName
 * @param {string} themeType
 */
function setTheme(themeName, themeType) {
    let html = document.documentElement.classList;
    let body = document.body.classList;

    html.forEach(i => {
        if (i.startsWith("theme-")) { html.remove(i); }
    });
    html.add(themeName);
    setCookie("theme", themeName);

    if (!body.contains(themeType)) { invertTheme(); }
}

/**
 * Apply setting option change
 * @param {string} optionName 
 */
function applyOptionChange(optionName) {
    if (optionName == "use_js") {
        window.location = window.location.pathname;
    }

    let tag = document.getElementById(optionName + "-related");
    if (tag !== null) {
        tag.disabled = !tag.disabled;
    }
}


/**
 * "onchange" function for settings checkbox
 * @param {PointerEvent} event
 * @param {string} optionName 
 */
function switchOption(event, optionName) {
    setBooleanCookie(optionName, event.target.checked);
    applyOptionChange(optionName);
}

/**
 * Copy code blocks content
 * @param {PointerEvent} event 
 */
function CopyCode(event) {
    var range = document.createRange();
    range.selectNode(event.target.parentElement.lastChild.lastChild);

    window.getSelection().removeAllRanges(); 
    window.getSelection().addRange(range); 
    document.execCommand("copy");
    window.getSelection().removeAllRanges();
}
