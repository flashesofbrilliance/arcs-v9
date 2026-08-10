<?php
/**
 * PRL Resins - spam keyword filter for Gravity Forms.
 * Generated from normalization/exclusions.json (SSOT). Do NOT hand-edit the array;
 * update exclusions.json + re-run `python3 exclusions.py --emit-php`.
 *
 * Marks a submission as spam (routed to the Spam folder, out of the inbox) when an UNAMBIGUOUS
 * spam term appears in a text field. Runs AFTER the honeypot + submission-speed-check.
 *
 * DELIBERATELY hard-spam ONLY. The anti-ICP 'sheet' seekers are NOT auto-flagged here, because on a
 * non-interactive form 'sheet' would false-positive on real 'datasheet' / 'spec sheet' requests (high-value
 * leads). Sheet seekers are handled without that risk by (a) the required pellets-vs-sheet form-factor field
 * and (b) the chatbot's soft prequal. Uses word boundaries so short tokens don't match inside words.
 */
add_filter( 'gform_entry_is_spam', function( $is_spam, $form, $entry ) {
    if ( $is_spam ) { return true; } // already flagged upstream (honeypot / speed check)

    $blocklist = array( 'affordable price', 'back link', 'backlink', 'bitcoin', 'boost your traffic', 'click here', 'crypto', 'digital marketing', 'first page of google', 'forex', 'gift card', 'grow your sales', 'guest blogging', 'guest post', 'increase your ranking', 'investment opportunity', 'lead generation service', 'limited time offer', 'link building', 'loan', 'make money', 'marketing services', 'rank higher', 'redesign your website', 'seo', 'unsubscribe', 'web design', 'website design', 'work from home' );

    $haystack = '';
    foreach ( $entry as $key => $value ) {
        if ( is_string( $value ) ) { $haystack .= ' ' . strtolower( $value ); }
    }
    foreach ( $blocklist as $kw ) {
        if ( $kw !== '' && preg_match( '/\b' . preg_quote( strtolower( $kw ), '/' ) . '\b/', $haystack ) ) {
            return true;
        }
    }
    return false;
}, 20, 3 );

