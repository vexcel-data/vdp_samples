def restrict_by_bounds(img, bounds, deg_per_pixel_wide, deg_per_pixel_high):
    min_x, min_y, max_x, max_y = bounds
    min_x_pixel, min_y_pixel = coord_to_pixel(min_x, min_y, bounds, deg_per_pixel_wide, deg_per_pixel_high)
    max_x_pixel, max_y_pixel = coord_to_pixel(max_x, max_y, bounds, deg_per_pixel_wide, deg_per_pixel_high)
    print(min_x_pixel, min_y_pixel)
    print(max_x_pixel, max_y_pixel)
    print(np.array(img).shape)
    img_restricted = np.array(img)[min_x_pixel:max_x_pixel, min_y_pixel:max_y_pixel]
    return Image.fromarray(img_restricted)

def degrees_per_pixel(bounds, pixels_wide, pixels_high):
    width_in_deg = bounds[2] - bounds[0]
    height_in_deg = bounds[3] - bounds[1]

    deg_per_pixel_wide = width_in_deg/pixels_wide
    deg_per_pixel_high = height_in_deg/pixels_high
    return deg_per_pixel_wide, deg_per_pixel_high

def pixel_to_coord(p_x, p_y, bounds, deg_per_pixel_wide, deg_per_pixel_high):
    c_x = bounds[0] + p_x*deg_per_pixel_wide
    c_y = bounds[1] + p_y*deg_per_pixel_high
    return [ c_x, c_y]


def coord_to_pixel(c_x, c_y, bounds, deg_per_pixel_wide, deg_per_pixel_high):
    p_x = int(np.round((c_x - bounds[0])/deg_per_pixel_high))
    p_y = int(np.round((c_y - bounds[1])/deg_per_pixel_wide))
    return [ p_x, p_y ]