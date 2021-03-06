const THEME_MODES = ["light-mode", "dark-mode"];

const BODY_CLASSES = document.body.classList;
const INV_THEME_BUTTON_CLASSES = document.getElementById("invert-theme-button").classList;
const CSS_RULES = document.getElementById("body_width-related").sheet.cssRules;

/**
 * Set some cookie value
 * @param {string} name Cookie name
 * @param {string} value Cookie value
 */
function setCookie(name, value) {
    document.cookie = `${name}=${value}; path=/; samesite=lax; expires=Tue, 19 Jan 2038 03:14:07 GMT`;
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
    setBooleanCookie("dark_mode", BODY_CLASSES.contains(THEME_MODES[0]));

    THEME_MODES.forEach(i => {
        BODY_CLASSES.toggle(i);
        INV_THEME_BUTTON_CLASSES.toggle(i);
    })
}

/**
 * Delete all theme classes and set new one
 * @param {DOMTokenList} classes 
 * @param {string} themeName 
 */
function SetThemeClass(classes, themeName) {
    classes.forEach(
        i => {
            if (i.endsWith("-theme")) { classes.remove(i); }
        }
    )
    classes.add(themeName);
}


/**
 * Set color theme and type
 * @param {string} themeName
 * @param {string} themeMode
 */
function setTheme(themeName, themeMode) {
    [BODY_CLASSES, INV_THEME_BUTTON_CLASSES].forEach(
        classes => { SetThemeClass(classes, themeName); }
    )

    setCookie("theme", themeName);
    if (!BODY_CLASSES.contains(themeMode)) { invertTheme(); }
}

/**
 * Apply boolean setting option change
 * @param {string} optionName 
 */
function applyBooleanOptionChange(optionName) {
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
    applyBooleanOptionChange(optionName);
}


/**
 * Copy code blocks content
 * @param {PointerEvent} event 
 */
function CopyCode(event) {
    let range = document.createRange();
    let node = event.target.parentElement.lastElementChild.lastElementChild;
    range.selectNode(node);

    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    document.execCommand("copy");
    window.getSelection().removeAllRanges();

    let copyButton = event.target.classList;
    copyButton.remove("copy-animation");
    event.target.offsetWidth;
    copyButton.add("copy-animation");
}


/**
 * change body width setting on mouseup range event
 * @param {MouseEvent} event 
 */
function ChangeBodyWidth(event) {
    let value = event.target.value;
    setCookie("body_width", value);
    CSS_RULES[0].style.setProperty("--body-width", value + "rem");
}


/**
 * edit number in range label
 * @param {Event} event 
 */
function ChangeRangeLabel(event) {
    event.target.labels.forEach(i => i.innerHTML = event.target.value);
}



const range = document.getElementById('body-width-range');
if (range !== null) {
    range.addEventListener("mouseup", ChangeBodyWidth);
    range.addEventListener("touchend", ChangeBodyWidth);
    range.addEventListener("input", ChangeRangeLabel);
}