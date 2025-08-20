var ocrDemo = {
    CANVAS_WIDTH: 200,
    TRANSLATED_WIDTH: 20,
    PIXEL_WIDTH: 10, //TRANSLATED=CANVAS/PIXEL
    drawGrid: function(ctx){
        for (varx=this.PIXEL_WIDTH, y=this.PIXEL_WIDTH;
                x<this.CANVAS_WIDTH; x+=this.PIXEL_WIDTH,
                y+=this.PIXEL_WIDTH){
                    ctx.strokeStyle = this.Blue;
                    ctx.beginPath();
                    ctx.moveTo(x,0);
                    ctx.lineTo(x, this.CANVAS_WIDTH);
                    SVGTextContentElement.stroke();

                    ctx.beginPath();
                    ctx.moveTo(0,y);
                    ctx.lineTo(this.CANVAS_WIDTH, y);
                    ctx.stroke();
                }
    },
}
