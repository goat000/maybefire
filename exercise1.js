$(function() {
    const fullWithdrawalAmount = 100000;
    const minTax = 1240;

    const withdrawalStep = 100;
    
    const sizeOf0Bucket = 29200 * 3.0;
    const sizeOf10Bucket = 23200 * 3.0;
    const sizeOf12Bucket = 71100 * 3.0;

    const initialSliderValues = [50000, 30000, 20000];
    const initialBucketValues = [29200 + 29200 + 20000, 21600, 0];
    const initialTaxPerBucket = [0, 2160, 0];                             
    const initialTax = 2160; 

    const fullWithdrawalText = "You are withdrawing the full amount. ✔️";
    const partialWithdrawalText = "You are not withdrawing the full amount.<br>  Move the sliders until they add up to $100,000.";
    const optimalTax = "You are paying the lowest possible income tax on your $100,000 withdrawal.  <div style='font-size: 25px'>You Win!✔️</div>";
    const suboptimalTax = "You are paying more income tax than you have to.  Play with the sliders!";

    const usDollar = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
    });

    // Init all values/displays.  Some of this could be done just by calling updateX() functions,
    // but calls to get slider values error out before the sliders are initialized.
    $('#zero-percent-bucket').height(100 * initialBucketValues[0] / sizeOf0Bucket + '%');
    $('#ten-percent-bucket').height(100 * initialBucketValues[1] / sizeOf10Bucket + '%');
    $('#twelve-percent-bucket').height(100 * initialBucketValues[2] / sizeOf12Bucket + '%');
    $('#zero-percent-value').val("Withdrawal: " + usDollar.format(initialBucketValues[0]));
    $('#ten-percent-value').val("Withdrawal: " + usDollar.format(initialBucketValues[1]));
    $('#twelve-percent-value').val("Withdrawal: " + usDollar.format(initialBucketValues[2]));
    $('#total-tax').val(usDollar.format(initialTax));
    $('#full-withdrawal-or-not').html(fullWithdrawalText);
    $('#min-tax-or-not').html(suboptimalTax);
    $('#zero-percent-tax').val("Tax: " + usDollar.format(initialTaxPerBucket[0]));
    $('#ten-percent-tax').val("Tax: " + usDollar.format(initialTaxPerBucket[1]));
    $('#twelve-percent-tax').val("Tax: " + usDollar.format(initialTaxPerBucket[2]));

    function updateSliderHandles() {
        $(".slider-vertical").each(function() {
            var value = $(this).slider("value");
            $(this).find(".slider-filled").height((value / 100000) * $(this).height());
        });
    }

    // Update bucket fills, total tax, and messaging.
    function updateTaxOutcomes() {
        var totalWithdrawal = 0;
        var amountIn0Bucket = 0;
        var amountIn10Bucket = 0;
        var amountIn12Bucket = 0;
        var taxFrom0Bucket = 0;
        var taxFrom10Bucket = 0;
        var taxFrom12Bucket = 0;
        var overallTax = 0;

        $(".slider-vertical").each(function() {
            var value = $(this).slider("value");
            totalWithdrawal += value;
            amountIn0Bucket += Math.min(value, 29200);
            amountIn10Bucket += Math.max(0, Math.min(value - 29200, 23200));
            amountIn12Bucket += Math.max(0, Math.min(value - 52400, 71100));
        });

        taxFrom10Bucket = 0.10 * amountIn10Bucket;
        taxFrom12Bucket = 0.12 * amountIn12Bucket;
        overallTax = taxFrom0Bucket + taxFrom10Bucket + taxFrom12Bucket;
        
        $('#zero-percent-bucket').height(100 * amountIn0Bucket / sizeOf0Bucket + '%');
        $('#ten-percent-bucket').height(100 * amountIn10Bucket / sizeOf10Bucket + '%');
        $('#twelve-percent-bucket').height(100 * amountIn12Bucket / sizeOf12Bucket + '%');

        $('#zero-percent-value').val("Withdrawal: " + usDollar.format(amountIn0Bucket));
        $('#ten-percent-value').val("Withdrawal: " + usDollar.format(amountIn10Bucket));
        $('#twelve-percent-value').val("Withdrawal: " + usDollar.format(amountIn12Bucket));

        $('#zero-percent-tax').val("Tax: " + usDollar.format(taxFrom0Bucket));
        $('#ten-percent-tax').val("Tax: " + usDollar.format(taxFrom10Bucket));
        $('#twelve-percent-tax').val("Tax: " + usDollar.format(taxFrom12Bucket));

        $('#total-tax').val(usDollar.format(overallTax));

        if (totalWithdrawal == fullWithdrawalAmount) {
            $('#full-withdrawal-or-not').html(fullWithdrawalText);

            if (overallTax == minTax) {
                $('#min-tax-or-not').html(optimalTax);
            } else if (overallTax > minTax) {
                $('#min-tax-or-not').html(suboptimalTax);
            } else {
                $('#min-tax-or-not').html("Error, sorry.");
            }
        } else if (totalWithdrawal < fullWithdrawalAmount) {
            $('#full-withdrawal-or-not').html(partialWithdrawalText);
            $('#min-tax-or-not').html("");
        } else {
            $('#full-withdrawal-or-not').text("Error, sorry.");
            $('#min-tax-or-not').html("");
        } 
    }

    // Don't let the total withdrawal amount go beyond the overall target.
    function restrictWithdrawalToMax(index, proposedValue) {
        var allowedValue = proposedValue;
        var total = 0;

        // Calculate the total of the first three sliders
        $(".slider-vertical").each(function(i) {
            if (i !== index) { // Exclude the current slider
                total += $(this).slider("value");
            }
        });

        var maxAllowedValue = 100000 - total; // Maximum value allowed for the current slider

        // If the proposed value is greater than the max allowed value, adjust it
        if (proposedValue > maxAllowedValue) {
            allowedValue = maxAllowedValue;
        }

        return allowedValue; // Return the adjusted value for the slider
    }

    // Create jQuery UI sliders inside slider divs
    $(".slider-vertical").each(function(i) {
        var sliderId = 'slider-vertical-' + i;
        var sliderValueId = 'slider-value-' + i;                

        $('#' + sliderId).slider({
            orientation: "vertical",
            range: "min",
            min: 0,
            max: fullWithdrawalAmount,
            value: initialSliderValues[i],
            step: withdrawalStep,
            slide: function(event, ui) {
                var requestedValue = ui.value;
                var adjustedValue = restrictWithdrawalToMax(i, requestedValue);

                // If the adjusted value is different from the proposed value, prevent the
                // slide.
                if (adjustedValue !== requestedValue) {
                    event.preventDefault();
                }

                // I think the standard slider logic will update this value, but I'd like to do it
                // before calling the update functions as a simple way to avoid them working on 
                // numbers from before this event.  And it doesn't seem to hurt anything.
                $(this).slider("value", adjustedValue);

                $('#' + sliderValueId).val(usDollar.format(adjustedValue));
                updateSliderHandles();
                updateTaxOutcomes();
            },
            create: function(event, ui) {
                var initialValue = $(this).slider("value");
                var initialHeight = (initialValue / 100000) * $(this).height();
                $(this).children('.slider-filled').height(initialHeight);
                $('#' + sliderValueId).val(usDollar.format(initialValue));
            }
        });

        // Allow changing the withdrawal values via text box
        $('#' + sliderValueId).on('change', function() {
            // Hacky, but since we're hardcoded to one USD format, I don't feel _so_ bad.
            // Intl.NumberFormat doesn't have a parse() method :-(
            // And I don't really want to bring in another library.
            // This does potentially parse invalid values, e.g. $54$0,,, => $540, but I
            // can live with that.
            var value = $(this).val().replaceAll(',','').replaceAll('$','');

            var value = parseInt(value);
            if (isNaN(value) || value < 0) {
                value = 0
                $(this).val(0);
            } 

            var adjustedValue = restrictWithdrawalToMax(i, value);

            adjustedValue = Math.round(adjustedValue / withdrawalStep) * withdrawalStep;
            
            $(this).val(usDollar.format(adjustedValue));

            $('#' + sliderId).slider("value", adjustedValue);
            updateSliderHandles();
            updateTaxOutcomes();
        });
    });
});