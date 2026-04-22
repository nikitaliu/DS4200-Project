(function () {
    const aliasMap = {
        "manchester by the sea": "manchester",
        "north attleborough": "north attleboro",
        "new marlboro": "new marlborough",
    };

    function normalizeTownName(value) {
        if (!value) {
            return "";
        }
        const normalized = String(value)
            .toLowerCase()
            .replace(/st\./g, "saint")
            .replace(/mt\./g, "mount")
            .replace(/[^a-z0-9]+/g, " ")
            .trim();
        return aliasMap[normalized] || normalized;
    }

    function titleCase(value) {
        return String(value)
            .toLowerCase()
            .split(/[\s-]+/)
            .filter(Boolean)
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ");
    }

    function formatCurrency(value) {
        if (!Number.isFinite(value)) {
            return "N/A";
        }
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            maximumFractionDigits: 0,
        }).format(value);
    }

    function formatShortCurrency(value) {
        if (!Number.isFinite(value)) {
            return "N/A";
        }
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            notation: "compact",
            maximumFractionDigits: 1,
        }).format(value);
    }

    function formatNumber(value, digits = 1) {
        if (!Number.isFinite(value)) {
            return "N/A";
        }
        return Number(value).toLocaleString("en-US", {
            minimumFractionDigits: digits,
            maximumFractionDigits: digits,
        });
    }

    function formatSigned(value, digits = 2) {
        if (!Number.isFinite(value)) {
            return "N/A";
        }
        return `${value >= 0 ? "+" : ""}${formatNumber(value, digits)}`;
    }

    function formatPercent(value, digits = 0) {
        if (!Number.isFinite(value)) {
            return "N/A";
        }
        return new Intl.NumberFormat("en-US", {
            style: "percent",
            minimumFractionDigits: digits,
            maximumFractionDigits: digits,
        }).format(value);
    }

    function labelizeVariable(variable) {
        const labelMap = {
            pricePerSqFt: "Price per sqft",
            ageOfHome: "Age of home",
            walkScore: "Walk score",
            bikeScore: "Bike score",
            transitScore: "Transit score",
            floodRisk: "Flood risk",
            fireRisk: "Fire risk",
            windRisk: "Wind risk",
            heatRisk: "Heat risk",
            airQualityRisk: "Air quality risk",
            livabilityComposite: "Livability composite",
            environmentalRiskComposite: "Environmental risk composite",
            priceToIncomeRatio: "Price-to-income ratio",
        };
        return labelMap[variable] || variable;
    }

    window.maUtils = {
        normalizeTownName,
        titleCase,
        formatCurrency,
        formatShortCurrency,
        formatNumber,
        formatSigned,
        formatPercent,
        labelizeVariable,
    };
})();
